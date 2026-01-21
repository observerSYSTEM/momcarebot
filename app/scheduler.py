from __future__ import annotations

from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .telegram import send_telegram, send_document
from .plan_reader import read_care_plan_from_excel, format_plan_for_telegram
from .pdf_builder import build_mom_care_pdf
from .logger import log_event

PLAN_PATH = "data/Mom_Care_Monthly_Support_Plan.xlsx"

# Change to 15 if you prefer
MONTHLY_TRANSFER_DAY = 1

TIMEZONE = "Europe/London"

PDF_DIR = Path("out")
PDF_DIR.mkdir(exist_ok=True)


def _safe(job: str, step: str, fn, *args, **kwargs):
    """
    Runs fn safely, logs success/error, and avoids crashing scheduler.
    """
    try:
        result = fn(*args, **kwargs)
        log_event(job, "SENT", message=step)
        return result
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        log_event(job, "ERROR", message=step, extra=err)

        # Try to notify you on Telegram (best effort)
        try:
            send_telegram(f"⚠️ MomCareBot {job} error at '{step}': {err}")
        except Exception:
            pass

        return None


def monthly_support_job() -> None:
    job = "monthly_support"
    log_event(job, "STARTED", message="Monthly job triggered")

    plan = _safe(job, "read_excel_plan", read_care_plan_from_excel, PLAN_PATH)
    if not plan:
        return

    stamp = datetime.now().strftime("%Y-%m")
    pdf_path = PDF_DIR / f"Mom_Care_Plan_{stamp}.pdf"

    built = _safe(job, "build_pdf", build_mom_care_pdf, plan, pdf_path)
    if built:
        _safe(job, "send_pdf_to_telegram", send_document, built, caption=f"📄 Mom Care Plan ({stamp})")

    msg = (
        "📅 Monthly Support Reminder\n"
        "Today is your scheduled transfer date.\n\n"
        + format_plan_for_telegram(plan)
    )
    _safe(job, "send_text_breakdown", send_telegram, msg)

    log_event(job, "DONE", message="Monthly job completed")


def weekly_call_job() -> None:
    job = "weekly_call"
    log_event(job, "STARTED", message="Weekly call job triggered")
    _safe(job, "send_call_reminder", send_telegram, "📞 MomCareBot: Reminder — call Mum today (weekly check-in).")
    log_event(job, "DONE", message="Weekly call job completed")


def emergency_savings_job() -> None:
    job = "emergency_savings"
    log_event(job, "STARTED", message="Emergency savings job triggered")

    plan = _safe(job, "read_excel_plan", read_care_plan_from_excel, PLAN_PATH)
    if not plan:
        _safe(job, "send_generic_emergency_reminder", send_telegram,
              "💰 MomCareBot: Reminder — put emergency savings aside this week.")
        log_event(job, "DONE", message="Emergency savings job completed")
        return

    emergency = next((i for i in plan.items if "emergency" in i.category.lower()), None)
    if emergency:
        line = f"💰 MomCareBot: Emergency savings reminder — £{emergency.amount_gbp:.0f}"
        if emergency.amount_ngn is not None:
            line += f" (≈ ₦{emergency.amount_ngn:,.0f})"
        _safe(job, "send_emergency_amount_reminder", send_telegram, line)
    else:
        _safe(job, "send_generic_emergency_reminder", send_telegram,
              "💰 MomCareBot: Reminder — put emergency savings aside this week.")

    log_event(job, "DONE", message="Emergency savings job completed")


def start_scheduler() -> None:
    sched = BlockingScheduler(timezone=TIMEZONE)

    sched.add_job(
        monthly_support_job,
        CronTrigger(day=MONTHLY_TRANSFER_DAY, hour=9, minute=0),
        id="monthly_support",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    sched.add_job(
        weekly_call_job,
        CronTrigger(day_of_week="sun", hour=18, minute=0),
        id="weekly_call",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    sched.add_job(
        emergency_savings_job,
        CronTrigger(day_of_week="fri", hour=19, minute=0),
        id="emergency_savings",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    log_event("system", "STARTED", message="Scheduler started")
    _safe("system", "startup_message", send_telegram, "✅ MomCareBot started. Logging + monthly PDF are active.")
    sched.start()
