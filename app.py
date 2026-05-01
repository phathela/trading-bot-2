import os
import logging
import time  # ADD THIS LINE
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from bybit_trader import BybitTrader
from datetime import datetime

load_dotenv()
app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_KEY = os.getenv('BYBIT_API_KEY', '')
API_SECRET = os.getenv('BYBIT_API_SECRET', '')
WEBHOOK_KEY = os.getenv('WEBHOOK_KEY', 'default_webhook_key')
SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')
TESTNET = os.getenv('BYBIT_TESTNET', 'True').lower() == 'true'

trader = BybitTrader(api_key=API_KEY, api_secret=API_SECRET, testnet=TESTNET)

# Simplified state tracking for single indicator
indicator_signals = {
    'last_action': None,
    'last_update': None,
    'trade_active': False,
    'position_side': None
}

def sync_position_state():
    """Query Bybit on startup and align state with the real position."""
    logger.info("=== Startup position sync: querying Bybit for real position state ===")
    try:
        result = trader.sync_position_from_exchange(symbol=SYMBOL)
        indicator_signals['trade_active'] = result['active']
        indicator_signals['position_side'] = result['side']
        if result['active']:
            logger.info(
                f"Startup sync complete — POSITION FOUND: "
                f"trade_active=True, position_side='{result['side']}'"
            )
        else:
            logger.info(
                "Startup sync complete — NO OPEN POSITION: "
                "trade_active=False, position_side=None"
            )
    except Exception as e:
        logger.error(f"Startup position sync failed — bot will start with default state: {str(e)}")

time.sleep(2)  # Wait 2 seconds to avoid Bybit rate limit on startup
sync_position_state()
trader.set_leverage(symbol=SYMBOL, leverage=8)  # Explicitly set 8x leverage on Bybit
logger.info(f"Bot initialized with leverage={trader.leverage}x, balance_usage={trader.balance_usage*100}%")
