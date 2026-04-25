"""
automation.py — Scheduling and trigger automation for lead enrichment

Supports:
1. Daily schedule (APScheduler at 9am)
2. Google Sheets watch (auto-process new rows)
3. Webhook trigger (for external integrations)
"""

import os
import logging
from datetime import datetime, time
from typing import Optional, Callable
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not installed. Schedule automation disabled.")


def get_scheduler() -> Optional["BackgroundScheduler"]:
    """Get configured scheduler instance."""
    if not SCHEDULER_AVAILABLE:
        return None
    
    scheduler = BackgroundScheduler(timezone="America/New_York")
    return scheduler


def schedule_daily_enrichment(
    scheduler: "BackgroundScheduler",
    hour: int = 9,
    minute: int = 0,
    job_id: str = "daily_lead_enrichment",
) -> None:
    """
    Schedule daily enrichment run at specified time.
    
    Args:
        scheduler: BackgroundScheduler instance
        hour: Hour of day (0-23), default 9am
        minute: Minute (0-59), default 0
        job_id: Unique identifier for this job
    """
    trigger = CronTrigger(hour=hour, minute=minute, timezone="America/New_York")
    
    scheduler.add_job(
        func=_run_daily_enrichment,
        trigger=trigger,
        id=job_id,
        name="Daily Lead Enrichment",
        replace_existing=True,
    )
    
    logger.info(f"Scheduled daily enrichment at {hour}:{minute:02d} ET")


def _run_daily_enrichment() -> dict:
    """Internal function to run daily enrichment and sync with Sheets."""
    from agent.pipeline import run_batch
    from integrations.sheets import read_unprocessed_leads, write_result_to_sheet
    
    logger.info("Starting daily lead enrichment run...")
    start_time = datetime.now()
    
    try:
        leads = read_unprocessed_leads()
        
        if not leads:
            logger.info("No unprocessed leads found in Google Sheets.")
            return {
                "status": "no_leads",
                "leads_found": 0,
                "processed": 0,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }
        
        logger.info(f"Found {len(leads)} unprocessed leads. Processing...")
        
        results = run_batch(leads)
        
        for lead, result in zip(leads, results):
            row_index = lead.get("_row_index")
            if row_index:
                write_result_to_sheet(result, lead, row_index)
        
        tier_counts = {"A": 0, "B": 0, "C": 0}
        for r in results:
            tier = r.get("tier")
            if tier in tier_counts:
                tier_counts[tier] += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Daily enrichment complete: {len(results)} processed, "
            f"Tier A: {tier_counts['A']}, B: {tier_counts['B']}, C: {tier_counts['C']}, "
            f"Duration: {duration:.1f}s"
        )
        
        return {
            "status": "success",
            "leads_found": len(leads),
            "processed": len(results),
            "tier_counts": tier_counts,
            "duration_seconds": duration,
        }
        
    except Exception as e:
        logger.error(f"Daily enrichment failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
        }


def start_scheduler() -> Optional["BackgroundScheduler"]:
    """Start the background scheduler with daily enrichment job."""
    scheduler = get_scheduler()
    
    if scheduler is None:
        logger.error("Scheduler not available. Install APScheduler: pip install apscheduler")
        return None
    
    schedule_daily_enrichment(scheduler, hour=9, minute=0)
    scheduler.start()
    
    logger.info("Scheduler started successfully.")
    return scheduler


def stop_scheduler(scheduler: "BackgroundScheduler") -> None:
    """Stop the scheduler gracefully."""
    scheduler.shutdown(wait=True)
    logger.info("Scheduler stopped.")


def trigger_manual_run() -> dict:
    """Manually trigger a lead enrichment run (for testing or webhook)."""
    return _run_daily_enrichment()


def get_next_run_time(scheduler: "BackgroundScheduler", job_id: str = "daily_lead_enrichment") -> Optional[str]:
    """Get the next scheduled run time for a job."""
    job = scheduler.get_job(job_id)
    if job and job.next_run_time:
        return job.next_run_time.isoformat()
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== Automation Test ===")
    
    if SCHEDULER_AVAILABLE:
        scheduler = start_scheduler()
        
        print(f"Next run: {get_next_run_time(scheduler)}")
        
        print("\nTriggering manual run...")
        result = trigger_manual_run()
        print(f"Result: {result}")
        
        stop_scheduler(scheduler)
    else:
        print("APScheduler not available. Testing direct run...")
        result = trigger_manual_run()
        print(f"Result: {result}")