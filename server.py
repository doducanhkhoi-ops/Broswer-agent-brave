import os
import sys

import uvicorn
from browser_use import Agent, Browser
from browser_use.llm.models import ChatGoogle, ChatOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

app = FastAPI(title="Brave Agent Bridge")


class TaskRequest(BaseModel):
    task: str


def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return ChatGoogle(model="gemini-3.6-flash", api_key=api_key)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)

    raise ValueError("Chưa cấu hình API Key trong file .env")


@app.post("/agent")
async def run_ai_task(req: TaskRequest):
    """Attach to an active Brave CDP session on port 9222, or launch a local Brave window."""
    print(f"\n[+] Nhận nhiệm vụ AI: {req.task}")
    try:
        llm = get_llm()

        try:
            browser = Browser(cdp_url="http://localhost:9222")
            print("[*] 👉 Đã kết nối TRỰC TIẾP vào cửa sổ Brave bạn đang mở!")
        except (OSError, RuntimeError, ValueError):
            print("[*] Không tìm thấy cổng 9222, mở cửa sổ Brave riêng biệt...")
            browser = Browser(executable_path=BRAVE_PATH, headless=False)

        agent = Agent(task=req.task, llm=llm, browser=browser)
        history = await agent.run()
        res = history.final_result()
        print(f"[+] Hoàn thành: {res}")
        return {"status": "success", "result": str(res)}
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"[!] Lỗi: {exc}")
        return {"status": "error", "message": str(exc)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8989)
