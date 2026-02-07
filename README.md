# MomCareBot 🧡

A personal Python automation tool built to support a retired parent with
structured monthly care, reminders, and documentation.

## Why this project exists

After my mother retired, I wanted a system that provides:
- predictable monthly support
- health and emergency planning
- peace of mind
- automation instead of stress

This tool turns responsibility into a structured system.

## Features

- Monthly support reminders (Telegram)
- Automatic PDF care plan generation
- Excel-based budget source
- Weekly call reminders
- Emergency savings reminders
- Activity logging
- Fully automated scheduler

## Tech stack

- Python
- APScheduler
- Telegram Bot API
- ReportLab (PDF generation)
- OpenPyXL (Excel parsing)

## Project structure

app/
main.py
scheduler.py
telegram.py
plan_reader.py
pdf_builder.py
logger.py


## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here


Run:

python -m app.main