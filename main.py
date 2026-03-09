"""
MAIN - Entry point for the entire system
Usage:
  python main.py           -> Start the scheduler (24/7 background)
  python main.py --scan    -> Run a single scan (test)
  python main.py --dash    -> Show the dashboard
  python main.py --setup   -> Show FaucetPay setup guide
"""
import sys
import os


def print_banner():
    print("""
+----------------------------------------------------------+
|          AUTONOMOUS EARNINGS SYSTEM v1.0                 |
|    Faucet Bot + Airdrop Scanner + Dashboard              |
+----------------------------------------------------------+
    """)


def setup_guide():
    print("""
+----------------------------------------------------------+
|                     SETUP GUIDE                          |
+----------------------------------------------------------+

STEP 1 -- Enter Your Wallet Address
-------------------------------------
  Open config.py:
    WALLET_ADDRESS = "0xYOUR_TRUST_WALLET_ADDRESS"
  In Trust Wallet: Settings -> Wallet -> Copy address

STEP 2 -- Create a FaucetPay Account
--------------------------------------
  1. Go to https://faucetpay.io
  2. Register (free)
  3. Copy your API key from Settings -> API Key
  4. Add it to config.py:
       FAUCETPAY_API_KEY = "your_api_key_here"
  5. Under "Add FaucetPay address", add your Trust Wallet
     address for each coin

STEP 3 -- Register on Faucet Sites
-------------------------------------
  Sign up on these sites and enter your FaucetPay address:
  * https://firefaucet.win        (Autoclaim - recommended!)
  * https://faucetcrypto.com
  * https://allcoins.pw
  * https://cointiply.com
  * https://freebitco.in

STEP 4 -- Start the Bot
--------------------------
  python main.py          (run 24/7)
  python main.py --dash   (view earnings)

QUICK START: Firefaucet.win is the best option!
  The Autoclaim feature means no manual clicking required.
""")


def run_scan_once():
    """Run a single scan."""
    print_banner()
    print("Running single scan...\n")

    try:
        from faucet_bot import run_faucet_scanner
        run_faucet_scanner()
    except Exception as e:
        print(f"Faucet bot error: {e}")

    print("\n" + "="*60 + "\n")

    try:
        from airdrop_scanner import run_airdrop_scanner
        run_airdrop_scanner()
    except Exception as e:
        print(f"Airdrop scanner error: {e}")


def run_dashboard():
    """Display the dashboard."""
    try:
        from dashboard import render_dashboard
        render_dashboard()
    except ImportError:
        print("The 'rich' library is required for the dashboard: pip install rich")
    except Exception as e:
        print(f"Dashboard error: {e}")


def run_all():
    """Start the full system (Scheduler)."""
    print_banner()

    # Config check
    from config import WALLET_ADDRESS
    if not WALLET_ADDRESS or WALLET_ADDRESS == "YOUR_WALLET_ADDRESS_HERE":
        print("ERROR: WALLET_ADDRESS is not set in config.py!")
        print("  Please enter your Trust Wallet address in config.py.")
        print("  Then run: python main.py")
        print()
        print("  For the setup guide run: python main.py --setup")
        return

    print(f"Wallet: {WALLET_ADDRESS[:10]}...{WALLET_ADDRESS[-4:]}")
    print()

    from scheduler import start_scheduler
    start_scheduler()


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--setup" in args:
        setup_guide()
    elif "--scan" in args:
        run_scan_once()
    elif "--dash" in args:
        run_dashboard()
    else:
        run_all()
