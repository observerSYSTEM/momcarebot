import os
import requests
from pathlib import Path


def _get_creds():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
    return token, chat_id


def send_telegram(message: str) -> None:
    token, chat_id = _get_creds()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat_id, "text": message})
    r.raise_for_status()


def send_document(file_path: str | Path, caption: str = "") -> None:
    token, chat_id = _get_creds()
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with file_path.open("rb") as f:
        files = {"document": (file_path.name, f)}
        data = {"chat_id": chat_id, "caption": caption} if caption else {"chat_id": chat_id}
        r = requests.post(url, data=data, files=files)
        r.raise_for_status()
