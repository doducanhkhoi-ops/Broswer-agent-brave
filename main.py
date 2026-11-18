import asyncio
import os
import sys

from browser_use import Agent, Browser
from browser_use.llm.models import ChatGoogle, ChatOpenAI
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles without closing underlying buffers
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("[*] Đang kết nối mô hình Google Gemini (gemini-3.6-flash)...")
        return ChatGoogle(model="gemini-3.6-flash", api_key=api_key)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("[*] Đang kết nối mô hình OpenAI...")
        return ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)

    print("[!] Không tìm thấy API Key nào trong file .env!")
    sys.exit(1)


async def run_task(task_description: str):
    llm = get_llm()

    browser = Browser(
        executable_path=BRAVE_PATH,
        headless=False,
    )

    agent = Agent(
        task=task_description,
        llm=llm,
        browser=browser,
    )

    print("\n[+] Khởi động trình duyệt Brave thành công!")
    print(f"[+] Nhiệm vụ: {task_description}\n")
    history = await agent.run()

    print("\n" + "=" * 20 + " KẾT QUẢ TỔNG HỢP " + "=" * 20)
    if hasattr(history, "final_result"):
        print(history.final_result())
    else:
        print(history)
    return history


if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Vào trang google.com, tìm kiếm 'thời tiết hôm nay tại Việt Nam' và tóm tắt kết quả."

    asyncio.run(run_task(task))
