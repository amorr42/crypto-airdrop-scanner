# ============================================================
# AUTONOMOUS EARNING BOT - CONFIG EXAMPLE
# Copy this file to config.py and fill in your values
# ============================================================

WALLET_ADDRESS = "0xYOUR_ETH_BNB_WALLET"       # ETH / BNB (EVM)
BTC_WALLET_ADDRESS = "YOUR_BTC_WALLET"           # Bitcoin
TRX_WALLET_ADDRESS = "YOUR_TRX_WALLET"           # TRON / USDT (TRC20)

FAUCETPAY_API_KEY = ""   # https://faucetpay.io

ENABLED_CHAINS = ["ETH", "BNB", "BTC", "LTC", "DOGE", "TRX"]

FAUCET_CLAIM_INTERVAL  = 300
AIRDROP_SCAN_INTERVAL  = 1800

LOG_FILE = "earnings.log"
DB_FILE  = "earnings.db"

MIN_AIRDROP_VALUE_USD = 10
MAX_ACCOUNTS_PER_DROP = 1

TELEGRAM_TOKEN   = ""
TELEGRAM_CHAT_ID = ""
