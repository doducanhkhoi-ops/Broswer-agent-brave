import asyncio
import os
import sys
import io
import webbrowser
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

from browser_use import Agent, Browser
from browser_use.llm.models import ChatGoogle, ChatOpenAI

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

app = FastAPI(title="Brave Agent Bridge")

class TaskRequest(BaseModel):
    task: str

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return ChatGoogle(model="gemini-3.6-flash", api_key=api_key)
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    else:
        raise ValueError("Chưa cấu hình API Key trong file .env")

@app.post("/agent")
async def run_ai_task(req: TaskRequest):
    """
    Ưu tiên kết nối thẳng vào cửa sổ Brave bạn đang dùng qua cổng 9222.
    Nếu bạn chưa mở cổng 9222 thì mới mở cửa sổ mới.
    """
    print(f"\n[+] Nhận nhiệm vụ AI: {req.task}")
    try:
        llm = get_llm()
        
        # Thử kết nối vào cửa sổ Brave BẠN ĐANG MỞ
        try:
            browser = Browser(cdp_url="http://localhost:9222")
            print("[*] 👉 Đã kết nối TRỰC TIẾP vào cửa sổ Brave bạn đang mở!")
        except Exception:
            print("[*] Không tìm thấy cổng 9222, mở cửa sổ Brave riêng biệt...")
            browser = Browser(executable_path=BRAVE_PATH, headless=False)

        agent = Agent(task=req.task, llm=llm, browser=browser)
        history = await agent.run()
        res = history.final_result()
        print(f"[+] Hoàn thành: {res}")
        return {"status": "success", "result": str(res)}
    except Exception as e:
        print(f"[!] Lỗi: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8989)
