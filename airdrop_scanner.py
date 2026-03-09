"""
AIRDROP SCANNER - Automatically scan and track active airdrops
Sources: CoinMarketCap, DeFiLlama, Airdrops.io RSS
"""
import requests
import sqlite3
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
from config import (
    WALLET_ADDRESS, DB_FILE, LOG_FILE,
    MIN_AIRDROP_VALUE_USD, ENABLED_CHAINS
)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s [AIRDROP] %(message)s")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}


def init_airdrop_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS airdrops (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT,
            project      TEXT,
            chain        TEXT,
            est_value_usd REAL,
            deadline     TEXT,
            status       TEXT,
            url          TEXT,
            participated INTEGER DEFAULT 0,
            found_at     TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_airdrop(name, project, chain, est_value, deadline, url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Duplicate check
    c.execute("SELECT id FROM airdrops WHERE name=? AND project=?", (name, project))
    if c.fetchone():
        conn.close()
        return False
    c.execute("""
        INSERT INTO airdrops (name, project, chain, est_value_usd, deadline, status, url, found_at)
        VALUES (?,?,?,?,?,?,?,?)
    """, (name, project, chain, est_value, deadline, "ACTIVE", url, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    logging.info(f"New airdrop found: {project} ({chain}) ~${est_value}")
    return True


def scan_defi_llama():
    """Scan the DeFiLlama airdrop list."""
    results = []
    try:
        r = requests.get(
            "https://defillama.com/airdrops",
            headers=HEADERS, timeout=15
        )
        soup = BeautifulSoup(r.text, "lxml")
        # DeFiLlama JSON data
        scripts = soup.find_all("script", {"id": "__NEXT_DATA__"})
        if scripts:
            data = json.loads(scripts[0].string)
            props = data.get("props", {}).get("pageProps", {}).get("airdrops", [])
            for item in props[:20]:
                results.append({
                    "name": item.get("name", ""),
                    "project": item.get("name", ""),
                    "chain": item.get("chain", "ETH"),
                    "value": item.get("totalAmount", 0),
                    "deadline": item.get("endDate", ""),
                    "url": f"https://defillama.com/airdrops"
                })
    except Exception as e:
        logging.warning(f"DeFiLlama scan error: {e}")
    return results


def scan_coinmarketcap_airdrops():
    """Scan the CoinMarketCap airdrop page."""
    results = []
    try:
        r = requests.get(
            "https://coinmarketcap.com/airdrop/",
            headers=HEADERS, timeout=15
        )
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("div", class_=lambda x: x and "airdrop" in x.lower())
        for card in cards[:15]:
            name = card.get_text(strip=True)[:50]
            if name:
                results.append({
                    "name": name,
                    "project": name,
                    "chain": "MULTI",
                    "value": 25.0,  # Default estimate
                    "deadline": "",
                    "url": "https://coinmarketcap.com/airdrop/"
                })
    except Exception as e:
        logging.warning(f"CMC scan error: {e}")
    return results


def run_airdrop_scanner():
    """Main airdrop scanning loop."""
    print("\nAIRDROP SCANNER STARTED")
    print(f"  Wallet: {WALLET_ADDRESS}")
    print(f"  Minimum value filter: ${MIN_AIRDROP_VALUE_USD}")
    print()

    if not WALLET_ADDRESS or WALLET_ADDRESS == "YOUR_WALLET_ADDRESS_HERE":
        print("ERROR: Enter your wallet address in config.py!")
        return

    init_airdrop_db()

    all_airdrops = []

    print("  Scanning DeFiLlama...")
    all_airdrops += scan_defi_llama()

    print("  Scanning CoinMarketCap...")
    all_airdrops += scan_coinmarketcap_airdrops()

    # Filter and save
    new_count = 0
    qualified = []
    for airdrop in all_airdrops:
        val = float(airdrop.get("value", 0) or 0)
        if val >= MIN_AIRDROP_VALUE_USD or val == 0:
            chain = airdrop.get("chain", "ETH")
            is_new = save_airdrop(
                airdrop["name"], airdrop["project"],
                chain, val,
                airdrop.get("deadline", ""),
                airdrop.get("url", "")
            )
            if is_new:
                new_count += 1
                qualified.append(airdrop)

    # Show results
    print(f"\nScan complete: {len(all_airdrops)} airdrops found, {new_count} new")
    print()
    print_airdrop_list()


def print_airdrop_list():
    """Display the airdrop list from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT project, chain, est_value_usd, deadline, url, participated
        FROM airdrops
        ORDER BY est_value_usd DESC
        LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()

    print("ACTIVE AIRDROP OPPORTUNITIES:")
    print("-" * 80)
    print(f"  {'Project':25s} {'Chain':8s} {'~Value':10s} {'Deadline':12s} {'Joined':8s}")
    print("-" * 80)
    for row in rows:
        project, chain, value, deadline, url, participated = row
        value_str = f"${value:.0f}" if value else "Unknown"
        deadline_str = deadline[:10] if deadline else "No deadline"
        participated_str = "Yes" if participated else "No"
        print(f"  {project:25s} {chain:8s} {value_str:10s} {deadline_str:12s} {participated_str}")
    print("-" * 80)
    print()
    print("To participate in these projects, visit the URLs above manually or use browser_bot.py.")


if __name__ == "__main__":
    run_airdrop_scanner()
