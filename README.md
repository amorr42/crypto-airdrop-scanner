# Crypto Airdrop Scanner & Faucet Bot

An autonomous system that periodically scans live airdrop listings and tracks
faucet claim activity, storing everything in a local SQLite database and
surfacing results through a Rich-powered terminal dashboard.

---

## What it does

| Component | Description |
|---|---|
| **Airdrop Scanner** | Scrapes DeFiLlama and CoinMarketCap for active airdrops, filters by a configurable minimum USD value, and saves new entries to the database. |
| **Faucet Bot** | Maintains a list of FaucetPay-compatible faucet sites, fetches live crypto prices via CoinGecko, queries your FaucetPay balance, and logs claim records to the database. |
| **Scheduler** | Runs both bots on configurable intervals (24/7) using background threads. |
| **Dashboard** | Renders a colour-coded terminal panel showing today's earnings, all-time totals, and the top 10 airdrops by estimated value. |

---

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Setup

### 1. Configure your wallet

Copy `config.example.py` to `config.py` and fill in your details:

```python
WALLET_ADDRESS    = "0xYOUR_TRUST_WALLET_ADDRESS"
FAUCETPAY_API_KEY = "your_faucetpay_api_key"
```

### 2. Create a FaucetPay account

1. Register at <https://faucetpay.io> (free).
2. Go to **Settings -> API Key** and copy your key.
3. Under **Add FaucetPay address**, add your wallet address for each coin
   (BTC, ETH, BNB, LTC, DOGE, TRX).

### 3. Register on faucet sites

Sign up at the following sites and enter your FaucetPay address:

- <https://firefaucet.win> — recommended; supports autoclaim
- <https://faucetcrypto.com>
- <https://allcoins.pw>
- <https://cointiply.com>
- <https://freebitco.in>

---

## Usage

```bash
# Start the scheduler (runs all bots continuously)
python main.py

# Run a single scan and exit (useful for testing)
python main.py --scan

# Open the terminal dashboard
python main.py --dash

# Print the setup guide
python main.py --setup
```

---

## Configuration reference

All settings live in `config.py` (do not commit this file if it contains secrets).

| Variable | Default | Description |
|---|---|---|
| `WALLET_ADDRESS` | — | Your crypto wallet address |
| `FAUCETPAY_API_KEY` | — | API key from faucetpay.io |
| `DB_FILE` | `earnings.db` | SQLite database path |
| `LOG_FILE` | `bot.log` | Log file path |
| `MIN_AIRDROP_VALUE_USD` | `10` | Minimum airdrop value to track |
| `ENABLED_CHAINS` | `["BTC","ETH","BNB"]` | Chains to query on FaucetPay |
| `FAUCET_CLAIM_INTERVAL` | `3600` | Faucet scan interval in seconds |
| `AIRDROP_SCAN_INTERVAL` | `21600` | Airdrop scan interval in seconds |

---

## Project structure

```
money/
├── main.py              # Entry point and CLI argument handling
├── airdrop_scanner.py   # Airdrop scraping and database storage
├── faucet_bot.py        # Faucet site list, price fetching, balance check
├── scheduler.py         # Background job scheduler
├── dashboard.py         # Rich terminal dashboard
├── config.py            # Your local configuration (not committed)
├── config.example.py    # Template configuration
└── requirements.txt     # Python dependencies
```

---

## Notes

- The airdrop scanner scrapes public web pages. Page structure changes on
  third-party sites may break parsing; check `bot.log` for warnings.
- Faucet sites that require CAPTCHA (Cointiply, FreeBitco.in) must be
  claimed manually in a browser. The bot tracks and lists them but cannot
  automate CAPTCHA solving.
- No private keys are stored or transmitted. The system only uses your
  public wallet address and a FaucetPay API key.
