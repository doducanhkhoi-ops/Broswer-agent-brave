<div align="center">

# Broswer-agent-brave

**Local FastAPI bridge and CLI runner for driving Brave Browser via `browser-use` and CDP.**

[![CI](https://github.com/doducanhkhoi-ops/Broswer-agent-brave/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/doducanhkhoi-ops/Broswer-agent-brave/actions/workflows/ci.yml)
[![Security Audit](https://github.com/doducanhkhoi-ops/Broswer-agent-brave/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/doducanhkhoi-ops/Broswer-agent-brave/actions/workflows/security.yml)
[![CodeQL](https://github.com/doducanhkhoi-ops/Broswer-agent-brave/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/doducanhkhoi-ops/Broswer-agent-brave/actions/workflows/codeql.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/doducanhkhoi-ops/Broswer-agent-brave)](./LICENSE)

</div>

---

Connects LLM agents (`Gemini` or `OpenAI`) directly to an active Brave window over Chrome DevTools Protocol (`localhost:9222`) or launches a local Brave instance on demand.

---

## Why Broswer-agent-brave?

- **CDP session reuse**: Attaches to an already-open Brave window on port `9222` to preserve logins and cookies.
- **Automatic fallback**: Launches a fresh Brave instance from `BRAVE_PATH` if CDP `9222` is unavailable.
- **Dual LLM provider**: Uses `GEMINI_API_KEY` (`gemini-3.6-flash`) by default and falls back to `OPENAI_API_KEY` (`gpt-4o-mini`).
- **Local HTTP bridge**: Exposes `POST /agent` on `127.0.0.1:8989` for external triggers and scripts.

---

## Feature Overview

| Component | Behavior |
| --- | --- |
| **HTTP Server** (`server.py`) | FastAPI endpoint `POST /agent` accepting `{"task": "..."}` on port `8989` |
| **CLI Runner** (`main.py`) | Single-shot async execution from command-line arguments |
| **Provider Resolver** | Selects `ChatGoogle` or `ChatOpenAI` from `.env` credentials |
| **Browser Connector** | Attaches to `http://localhost:9222` with fallback to local Brave binary |

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/doducanhkhoi-ops/Broswer-agent-brave.git
cd Broswer-agent-brave
pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key
# Optional fallback:
# OPENAI_API_KEY=your_openai_api_key
```

### 3. Run

**CLI mode:**

```bash
python main.py "Go to news.ycombinator.com and summarize the top 3 posts"
```

**HTTP Bridge mode:**

```bash
# Optional: start Brave with CDP enabled
brave.exe --remote-debugging-port=9222

# Start FastAPI bridge on 127.0.0.1:8989
python server.py
```

```bash
curl -X POST http://127.0.0.1:8989/agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Open github.com and check notifications"}'
```

Output:

```json
{
  "status": "success",
  "result": "..."
}
```

---

## Testing & Security

```bash
python -m unittest discover -s tests -v
```

| Check | Tool | Scope |
| --- | --- | --- |
| **Unit & API Tests** | `pytest` (`3.10`, `3.11`, `3.12`) | LLM selection, `/agent` endpoint, CDP-to-local fallback, error handling |
| **SAST** | GitHub CodeQL | Static vulnerability analysis on Python source |
| **Security Lint** | `bandit` + `ruff` | Exception hygiene, static security checks |

---

## License

[Apache License 2.0](./LICENSE)
