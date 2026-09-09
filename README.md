# Brave LLM Agent Bridge

A lightweight local automation bridge connecting LLMs (Google Gemini / OpenAI) directly to your active **Brave Browser** session via Chrome DevTools Protocol (CDP).

---

## The Idea: Extending "Awesome LLM Apps"

This project was built upon the browser automation recipes in [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) and powered by [browser-use](https://github.com/browser-use/browser-use).

Standard open-source templates run agents in disposable, isolated browser instances. In daily workflows, that breaks down:

| Feature | Awesome LLM Apps (Default Demo) | This Implementation (Brave Bridge) |
|---|---|---|
| **Session** | Stateless, blank Chromium window | Attaches to your live Brave window (`localhost:9222`) |
| **Authentication** | Blocked by logins, 2FA, Captchas | Inherits your active logins (Google, Facebook, YouTube) |
| **Interface** | One-shot CLI run | Persistent FastAPI server (`:8989`) callable from any app |
| **Execution** | Pure screenshot-to-LLM loop (slow) | Hybrid: LLM reasoning + Direct CDP/DOM events (instant) |

---

## Prerequisites

- **OS:** Windows 10/11 (macOS / Linux compatible by updating executable path)
- **Browser:** [Brave Browser](https://brave.com/)
- **Python:** 3.11+
- **API Key:** Google Gemini API Key or OpenAI API Key

---

## Step-by-Step Setup Guide

### 1. Launch Brave with Remote Debugging

Before starting the agent, Brave must run with debugging port `9222` enabled.

1. Close all running Brave windows:
   ```powershell
   Stop-Process -Name "brave" -Force -ErrorAction SilentlyContinue
   ```

2. Start Brave with the debugging flag:
   ```powershell
   & "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
   ```

   **Desktop Shortcut Setup:**  
   Right-click Desktop -> **New** -> **Shortcut** -> Target:  
   `"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222`

3. Verify: open `http://localhost:9222/json/version` in your browser. It should return a JSON status object.

---

### 2. Clone & Install Dependencies

```powershell
git clone https://github.com/doducanhkhoi-ops/brave-llm-agent.git
cd brave-llm-agent

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

---

### 3. Configure API Key

1. Create your `.env` file from the example:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Add your Gemini API key (or OpenAI key) in `.env`:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

---

## Usage Modes

### Mode A: Persistent FastAPI Server (Recommended)

Keeps a local bridge server listening on port `8989` so background scripts, OS hotkeys, or other AI agents can dispatch web tasks on demand.

1. Start the server:
   ```powershell
   python server.py
   ```

2. Send tasks via PowerShell or cURL:

   **PowerShell:**
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8989/agent" `
     -Method Post `
     -ContentType "application/json" `
     -Body '{"task": "Go to YouTube and search for Lo-Fi chill beats"}'
   ```

   **cURL:**
   ```bash
   curl -X POST http://127.0.0.1:8989/agent \
     -H "Content-Type: application/json" \
     -d '{"task": "Check my upcoming events on Google Calendar"}'
   ```

### Mode B: Direct CLI Runner

Run a single task directly:

```powershell
python main.py "Open Google Calendar and list my meetings for today"
```

---

## Project Structure

```text
├── .env.example          # Sample environment variables
├── .gitignore            # Ignores .env, virtualenvs, cache
├── requirements.txt      # Minimal dependencies
├── main.py               # Standalone CLI task runner
├── server.py             # FastAPI bridge server (:8989)
└── README.md             # Project documentation
```

---

## Troubleshooting

| Issue | Cause & Fix |
|---|---|
| `Cannot connect to localhost:9222` | Brave was already running before adding the flag. Run `Stop-Process -Name "brave" -Force` and relaunch. |
| `Brave path not found` | If Brave is installed in AppData, update `BRAVE_PATH` in `server.py` and `main.py`. |
| `Script execution disabled` (PowerShell) | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your terminal session. |

---

## Acknowledgements

- [Shubham Saboo / awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) for practical AI agent architecture recipes.
- [browser-use](https://github.com/browser-use/browser-use) for the underlying web interaction agent engine.

## License
Apache-2.0