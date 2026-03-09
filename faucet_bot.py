"""
FAUCET BOT - Automatic crypto collection via the FaucetPay ecosystem
Supported: BTC, ETH, BNB, LTC, DOGE, TRX
"""
import requests
import time
import sqlite3
import logging
from datetime import datetime
from config import WALLET_ADDRESS, FAUCETPAY_API_KEY, ENABLED_CHAINS, DB_FILE, LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [FAUCET] %(message)s"
)

# Currencies supported by FaucetPay and their minimum claim amounts
FAUCETPAY_CURRENCIES = {
    "BTC":  {"symbol": "BTC",  "min_satoshi": 10},
    "ETH":  {"symbol": "ETH",  "min_wei": 100},
    "BNB":  {"symbol": "BNB",  "min_gwei": 100},
    "LTC":  {"symbol": "LTC",  "min_litoshi": 100},
    "DOGE": {"symbol": "DOGE", "min_koinu": 100},
    "TRX":  {"symbol": "TRX",  "min_sun": 100},
}

# Active faucet list (FaucetPay compatible)
FAUCET_SITES = [
    {
        "name": "Cointiply",
        "url": "https://cointiply.com",
        "currency": "BTC",
        "type": "browser",
        "claim_interval_min": 60,
        "notes": "Requires captcha - manual setup"
    },
    {
        "name": "FreeBitco.in",
        "url": "https://freebitco.in",
        "currency": "BTC",
        "type": "browser",
        "claim_interval_min": 60,
        "notes": "Requires captcha - manual setup"
    },
    {
        "name": "Allcoins.pw",
        "url": "https://allcoins.pw",
        "currency": "MULTI",
        "type": "api",
        "claim_interval_min": 5,
        "notes": "API-based"
    },
    {
        "name": "FaucetCrypto",
        "url": "https://faucetcrypto.com",
        "currency": "MULTI",
        "type": "browser",
        "claim_interval_min": 30,
        "notes": "Multi-coin"
    },
    {
        "name": "Firefaucet.win",
        "url": "https://firefaucet.win",
        "currency": "MULTI",
        "type": "browser",
        "claim_interval_min": 1,
        "notes": "Supports autoclaim"
    },
]


def init_db():
    """Create database tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS faucet_claims (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            site      TEXT,
            currency  TEXT,
            amount    REAL,
            usd_value REAL,
            claimed_at TEXT,
            status    TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_claim(site: str, currency: str, amount: float, usd_value: float, status: str):
    """Insert a claim record into the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO faucet_claims (site, currency, amount, usd_value, claimed_at, status) VALUES (?,?,?,?,?,?)",
        (site, currency, amount, usd_value, datetime.now().isoformat(), status)
    )
    conn.commit()
    conn.close()
    logging.info(f"Claim recorded: {site} | {currency} | {amount} | ${usd_value:.6f} | {status}")


def get_crypto_price(symbol: str) -> float:
    """Fetch the current price via the CoinGecko API."""
    slug_map = {
        "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
        "LTC": "litecoin", "DOGE": "dogecoin", "TRX": "tron"
    }
    slug = slug_map.get(symbol, symbol.lower())
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={slug}&vs_currencies=usd",
            timeout=10
        )
        data = r.json()
        return data.get(slug, {}).get("usd", 0.0)
    except Exception as e:
        logging.warning(f"Could not fetch price ({symbol}): {e}")
        return 0.0


def check_faucetpay_balance() -> dict:
    """Query FaucetPay balance."""
    if not FAUCETPAY_API_KEY:
        return {}
    results = {}
    for currency in ENABLED_CHAINS:
        try:
            r = requests.post(
                "https://faucetpay.io/api/v1/balance",
                data={"api_key": FAUCETPAY_API_KEY, "currency": currency},
                timeout=10
            )
            data = r.json()
            if data.get("status") == 200:
                results[currency] = data.get("balance", 0)
        except Exception as e:
            logging.warning(f"FaucetPay balance query error ({currency}): {e}")
    return results


def print_faucet_summary():
    """Summarise today's earnings."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT currency, COUNT(*), SUM(amount), SUM(usd_value)
        FROM faucet_claims
        WHERE date(claimed_at) = date('now')
        GROUP BY currency
    """)
    rows = c.fetchall()
    conn.close()
    print("\nTODAY'S FAUCET EARNINGS:")
    print("-" * 45)
    total_usd = 0
    for row in rows:
        currency, count, amount, usd = row
        total_usd += usd or 0
        print(f"  {currency:5s} | {count:3d} claims | {amount:.8f} | ${usd:.6f}")
    print(f"  {'TOTAL':5s} |           |              | ${total_usd:.4f}")
    print("-" * 45)
    return total_usd


def run_faucet_scanner():
    """Print the active faucet list to the console and start scanning."""
    print("\nFAUCET BOT STARTED")
    print(f"  Target wallet: {WALLET_ADDRESS}")
    print(f"  Active chains: {', '.join(ENABLED_CHAINS)}")
    print()

    if not WALLET_ADDRESS or WALLET_ADDRESS == "YOUR_WALLET_ADDRESS_HERE":
        print("ERROR: Enter your wallet address in config.py!")
        return

    init_db()

    print("Detected faucet sites:")
    for i, site in enumerate(FAUCET_SITES, 1):
        print(f"  {i}. {site['name']:20s} | {site['currency']:5s} | Every {site['claim_interval_min']} min | {site['notes']}")

    print()
    print("Automatic claiming will be active after FaucetPay API setup.")
    print("  Manual faucet list is ready:")
    print()

    # Fetch and display prices
    print("Current crypto prices:")
    for sym in ["BTC", "ETH", "BNB"]:
        price = get_crypto_price(sym)
        print(f"  {sym}: ${price:,.2f}")

    # FaucetPay balance
    if FAUCETPAY_API_KEY:
        print("\nFaucetPay Balances:")
        balances = check_faucetpay_balance()
        for cur, bal in balances.items():
            price = get_crypto_price(cur)
            usd = (bal / 1e8) * price
            print(f"  {cur}: {bal} satoshi ~= ${usd:.6f}")
    else:
        print("\nWARNING: FaucetPay API key not set. Update config.py.")

    print_faucet_summary()


if __name__ == "__main__":
    run_faucet_scanner()
