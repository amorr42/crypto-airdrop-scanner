"""
SCHEDULER - Task scheduler that runs all bots 24/7
"""
import schedule
import time
import threading
import logging
from datetime import datetime
from config import FAUCET_CLAIM_INTERVAL, AIRDROP_SCAN_INTERVAL, LOG_FILE

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s"
)


def run_faucet_job():
    """Run the faucet bot."""
    try:
        from faucet_bot import run_faucet_scanner
        logging.info("Faucet scan started")
        run_faucet_scanner()
        logging.info("Faucet scan complete")
    except Exception as e:
        logging.error(f"Faucet job error: {e}")


def run_airdrop_job():
    """Run the airdrop scanner."""
    try:
        from airdrop_scanner import run_airdrop_scanner
        logging.info("Airdrop scan started")
        run_airdrop_scanner()
        logging.info("Airdrop scan complete")
    except Exception as e:
        logging.error(f"Airdrop job error: {e}")


def run_in_thread(func):
    """Run a task in a separate thread."""
    t = threading.Thread(target=func, daemon=True)
    t.start()


def start_scheduler():
    """Configure and start the scheduler."""
    print(f"\nSCHEDULER STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Faucet scan: every {FAUCET_CLAIM_INTERVAL//60} minutes")
    print(f"  Airdrop scan: every {AIRDROP_SCAN_INTERVAL//60} minutes")
    print("  Press CTRL+C to stop\n")

    # First run (immediate)
    run_in_thread(run_faucet_job)
    time.sleep(5)
    run_in_thread(run_airdrop_job)

    # Scheduled tasks
    schedule.every(FAUCET_CLAIM_INTERVAL).seconds.do(
        lambda: run_in_thread(run_faucet_job)
    )
    schedule.every(AIRDROP_SCAN_INTERVAL).seconds.do(
        lambda: run_in_thread(run_airdrop_job)
    )

    # Daily summary (every morning at 09:00)
    schedule.every().day.at("09:00").do(
        lambda: run_in_thread(lambda: print(
            f"\nDAILY SUMMARY - {datetime.now().strftime('%Y-%m-%d')}"
        ))
    )

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    start_scheduler()
