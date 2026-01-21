import os
from dotenv import load_dotenv
from .scheduler import start_scheduler
from .telegram import send_telegram

def main():
    load_dotenv()
    send_telegram("MomCareBot is live ✅ Reminders are active.")
    start_scheduler()

if __name__ == "__main__":
    main()
