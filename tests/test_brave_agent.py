import importlib
import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


def _ensure_browser_use_stub():
    if "browser_use" in sys.modules:
        return
    browser_use = types.ModuleType("browser_use")
    browser_use.Agent = MagicMock()
    browser_use.Browser = MagicMock()

    llm_pkg = types.ModuleType("browser_use.llm")
    llm_models = types.ModuleType("browser_use.llm.models")
    llm_models.ChatGoogle = MagicMock(side_effect=lambda **kw: ("google", kw))
    llm_models.ChatOpenAI = MagicMock(side_effect=lambda **kw: ("openai", kw))

    sys.modules["browser_use"] = browser_use
    sys.modules["browser_use.llm"] = llm_pkg
    sys.modules["browser_use.llm.models"] = llm_models


_ensure_browser_use_stub()
server = importlib.import_module("server")
main = importlib.import_module("main")


class TestProviderSelection(unittest.TestCase):
    def test_server_prefers_gemini_over_openai(self):
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "g-key", "OPENAI_API_KEY": "o-key"}, clear=True),
            patch.object(server, "ChatGoogle", return_value="gemini-client") as mock_g,
        ):
            res = server.get_llm()
        self.assertEqual(res, "gemini-client")
        mock_g.assert_called_once_with(model="gemini-3.6-flash", api_key="g-key")

    def test_server_falls_back_to_openai(self):
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "o-key"}, clear=True),
            patch.object(server, "ChatOpenAI", return_value="openai-client") as mock_o,
        ):
            res = server.get_llm()
        self.assertEqual(res, "openai-client")
        mock_o.assert_called_once_with(model="gpt-4o-mini", api_key="o-key")

    def test_server_raises_when_no_api_key(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            self.assertRaises(ValueError),
        ):
            server.get_llm()

    def test_main_exits_when_no_api_key(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            self.assertRaises(SystemExit) as ctx,
        ):
            main.get_llm()
        self.assertEqual(ctx.exception.code, 1)


class TestAgentEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(server.app)

    def test_agent_connects_via_cdp_and_returns_result(self):
        mock_history = MagicMock()
        mock_history.final_result.return_value = "Task done"
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_history)

        with (
            patch.object(server, "get_llm", return_value="llm"),
            patch.object(server, "Browser", return_value="cdp-browser") as mock_browser,
            patch.object(server, "Agent", return_value=mock_agent),
        ):
            resp = self.client.post("/agent", json={"task": "Open example.com"})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "success", "result": "Task done"})
        mock_browser.assert_called_once_with(cdp_url="http://localhost:9222")

    def test_agent_falls_back_to_local_brave_when_cdp_unavailable(self):
        mock_history = MagicMock()
        mock_history.final_result.return_value = "Fallback ok"
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_history)

        with (
            patch.object(server, "get_llm", return_value="llm"),
            patch.object(server, "Browser", side_effect=[OSError("no cdp"), "local-browser"]) as mock_browser,
            patch.object(server, "Agent", return_value=mock_agent),
        ):
            resp = self.client.post("/agent", json={"task": "Search weather"})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "success", "result": "Fallback ok"})
        self.assertEqual(mock_browser.call_count, 2)

    def test_agent_returns_error_payload_when_key_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            resp = self.client.post("/agent", json={"task": "Search"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "error")
        self.assertIn("API Key", body["message"])


if __name__ == "__main__":
    unittest.main()
