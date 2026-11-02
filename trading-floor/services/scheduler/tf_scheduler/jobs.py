"""Clock publishes ticks. Job callables do not import an adapter."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from tf_scheduler.ticks import heartbeat, schedule_tick


def build_scheduler(mode: str) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="America/New_York")
    scheduler.add_job(
        lambda: schedule_tick(mode, "daily_plan"),
        CronTrigger(hour=9, minute=0, timezone="America/New_York"),
        id="daily_plan",
    )
    scheduler.add_job(
        lambda: schedule_tick(mode, "nightly_review"),
        CronTrigger(hour=18, minute=0, timezone="America/New_York"),
        id="nightly_review",
    )
    scheduler.add_job(
        lambda: heartbeat(mode),
        "interval",
        seconds=5,
        id="heartbeat",
    )
    return scheduler
