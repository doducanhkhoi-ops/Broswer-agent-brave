import asyncio
import os
import sys
import io

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.llm.models import ChatGoogle, ChatOpenAI

load_dotenv()

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("[*] Đang kết nối mô hình Google Gemini (gemini-3.6-flash)...")
        # Sử dụng model gemini-3.6-flash đúng với thông báo của Google API
        return ChatGoogle(model="gemini-3.6-flash", api_key=api_key)

    elif os.getenv("OPENAI_API_KEY"):
        print("[*] Đang kết nối mô hình OpenAI...")
        return ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    else:
        print("[!] Không tìm thấy API Key nào trong file .env!")
        sys.exit(1)

async def run_task(task_description: str):
    llm = get_llm()

    browser = Browser(
        executable_path=BRAVE_PATH,
        headless=False
    )

    agent = Agent(
        task=task_description,
        llm=llm,
        browser=browser
    )

    print(f"\n[+] Khởi động trình duyệt Brave thành công!")
    print(f"[+] Nhiệm vụ: {task_description}\n")
    history = await agent.run()

    print("\n" + "="*20 + " KẾT QUẢ TỔNG HỢP " + "="*20)
    try:
        print(history.final_result())
    except Exception:
        print(history)
    return history

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Vào trang google.com, tìm kiếm 'thời tiết hôm nay tại Việt Nam' và tóm tắt kết quả."

    asyncio.run(run_task(task))
