import os
import logging
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

indicator_signals = {
    'indicator_a': None,
    'indicator_b': None,
    'last_update': None,
    'trade_active': False,
    'position_side': None  # 'long', 'short', or None
}


def sync_position_state():
    """Query Bybit and align indicator_signals with the real position state.

    Called both on startup and at the start of every process_trade_signals()
    invocation so that positions closed externally (stop loss, manual close,
    another bot) are detected before any trade action is attempted.
    """
    logger.info("=== Position sync: querying Bybit for real position state ===")
    try:
        result = trader.sync_position_from_exchange(symbol=SYMBOL)
        indicator_signals['trade_active'] = result['active']
        indicator_signals['position_side'] = result['side']

        if result['active']:
            logger.info(
                f"Position sync complete — POSITION FOUND: "
                f"trade_active=True, position_side='{result['side']}'"
            )
        else:
            logger.info(
                "Position sync complete — NO OPEN POSITION: "
                "trade_active=False, position_side=None"
            )
    except Exception as e:
        logger.error(f"Position sync failed — proceeding with current state: {str(e)}")


try:
    trader.balance_usage = 0.90
    trader.set_leverage(symbol=SYMBOL, leverage=8)
    sync_position_state()
except Exception as e:
    logger.error(f"Startup initialization failed: {str(e)}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        auth_key = request.headers.get('X-Webhook-Key')
        if auth_key != WEBHOOK_KEY:
            logger.warning(f"Unauthorized webhook attempt with key: {auth_key}")
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        logger.info(f"Webhook received: {data}")

        indicator = data.get('indicator')
        signal = data.get('signal')

        if indicator not in ['indicator_a', 'indicator_b'] or signal not in ['Buy', 'Sell']:
            return jsonify({'error': 'Invalid indicator or signal'}), 400

        indicator_signals[indicator] = signal
        indicator_signals['last_update'] = datetime.now().isoformat()

        logger.info(f"{indicator}: {signal}")
        logger.info(f"Indicator A: {indicator_signals['indicator_a']}, Indicator B: {indicator_signals['indicator_b']}")

        result = process_trade_signals()

        return jsonify({
            'status': 'received',
            'indicator_signals': indicator_signals,
            'trade_action': result
        }), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/3commas/a', methods=['POST'])
def webhook_3commas_a():
    """Accept 3Commas format webhooks for Indicator A"""
    return process_3commas_webhook('indicator_a')

@app.route('/webhook/3commas/b', methods=['POST'])
def webhook_3commas_b():
    """Accept 3Commas format webhooks for Indicator B"""
    return process_3commas_webhook('indicator_b')

def process_3commas_webhook(indicator):
    """Convert 3Commas format to bot format for specified indicator"""
    try:
        data = request.get_json(force=True, silent=True)
        logger.info(f"3Commas webhook received for {indicator}: {data}")

        if data is None:
            logger.warning(f"Failed to parse JSON body for {indicator} webhook — missing or invalid Content-Type")
            return jsonify({'error': 'Invalid or missing JSON body. Ensure the request body is valid JSON.'}), 400

        action = data.get('action', '').lower()

        # Convert 3Commas action to buy/sell signal
        if action == 'enter_long':
            signal = 'Buy'
        elif action == 'enter_short':
            signal = 'Sell'
        elif action == 'close_long':
            signal = 'Sell'
        elif action == 'close_short':
            signal = 'Buy'
        else:
            logger.warning(f"Unknown 3Commas action: {action}")
            return jsonify({'error': f'Unknown action: {action}'}), 400

        logger.info(f"3Commas action converted: {action} → {signal} for {indicator}")

        # Set the specified indicator signal
        indicator_signals[indicator] = signal
        indicator_signals['last_update'] = datetime.now().isoformat()

        logger.info(f"{indicator}: {signal}")
        logger.info(f"Indicator A: {indicator_signals['indicator_a']}, Indicator B: {indicator_signals['indicator_b']}")

        # Process the signals (will only execute if both aligned)
        result = process_trade_signals()

        return jsonify({
            'status': 'received',
            'indicator': indicator,
            'action': action,
            'signal': signal,
            'trade_action': result,
            'indicator_signals': indicator_signals
        }), 200

    except Exception as e:
        logger.error(f"Error processing 3Commas webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_trade_signals():
    """Process signals from both indicators and execute trades.

    Rules:
    - No position open:
        * Either signal is None → Wait
        * Both Buy → Open LONG
        * Both Sell → Open SHORT
        * One Buy + one Sell (disagree) → Wait

    - LONG position open:
        * Either signal is None → Hold LONG (wait for clarity)
        * Both Buy → Hold LONG
        * Both Sell OR one Buy + one Sell (disagree) → Close LONG immediately

    - SHORT position open:
        * Either signal is None → Hold SHORT (wait for clarity)
        * Both Sell → Hold SHORT
        * Both Buy OR one Buy + one Sell (disagree) → Close SHORT immediately
    """
    # Sync with Bybit before acting so that positions closed externally
    # (stop loss, manual close, another bot) are detected immediately,
    # preventing 110017 "current position is zero" errors.
    sync_position_state()

    signal_a = indicator_signals['indicator_a']
    signal_b = indicator_signals['indicator_b']
    trade_active = indicator_signals['trade_active']
    position_side = indicator_signals['position_side']

    logger.info(f"Processing signals — A={signal_a}, B={signal_b}, active={trade_active}, side={position_side}")

    # ── No position open ────────────────────────────────────────────────────
    if not trade_active:
        if signal_a is None or signal_b is None:
            logger.info("Waiting for both indicators before opening a position")
            return None

        if signal_a == 'Buy' and signal_b == 'Buy':
            logger.info("Both indicators signal BUY — opening LONG position")
            if trader.open_position(symbol=SYMBOL, side='Buy'):
                indicator_signals['trade_active'] = True
                indicator_signals['position_side'] = 'long'
                return 'OPEN_LONG'
            return 'OPEN_LONG_FAILED'

        if signal_a == 'Sell' and signal_b == 'Sell':
            logger.info("Both indicators signal SELL — opening SHORT position")
            if trader.open_position(symbol=SYMBOL, side='Sell'):
                indicator_signals['trade_active'] = True
                indicator_signals['position_side'] = 'short'
                return 'OPEN_SHORT'
            return 'OPEN_SHORT_FAILED'

        # One Buy + one Sell: indicators disagree — wait
        logger.info(f"Indicators disagree (A={signal_a}, B={signal_b}) — waiting for alignment")
        return None

    # ── LONG position is open ───────────────────────────────────────────────
    if position_side == 'long':
        # Hold if either signal is missing — not enough information to act
        if signal_a is None or signal_b is None:
            logger.info(f"LONG position: signal missing (A={signal_a}, B={signal_b}) — holding")
            return 'HOLD_LONG'

        # Hold if both still agree on BUY
        if signal_a == 'Buy' and signal_b == 'Buy':
            logger.info("LONG position: both indicators still BUY — holding")
            return 'HOLD_LONG'

        # Close on disagreement (one Buy + one Sell) or both flipping to Sell
        logger.info(
            f"LONG position: indicators disagree or flipped (A={signal_a}, B={signal_b}) "
            "— closing LONG immediately"
        )
        if trader.close_position(symbol=SYMBOL):
            indicator_signals['trade_active'] = False
            indicator_signals['position_side'] = None
            return 'CLOSE_LONG'
        return 'CLOSE_LONG_FAILED'

    # ── SHORT position is open ──────────────────────────────────────────────
    if position_side == 'short':
        # Hold if either signal is missing — not enough information to act
        if signal_a is None or signal_b is None:
            logger.info(f"SHORT position: signal missing (A={signal_a}, B={signal_b}) — holding")
            return 'HOLD_SHORT'

        # Hold if both still agree on SELL
        if signal_a == 'Sell' and signal_b == 'Sell':
            logger.info("SHORT position: both indicators still SELL — holding")
            return 'HOLD_SHORT'

        # Close on disagreement (one Buy + one Sell) or both flipping to Buy
        logger.info(
            f"SHORT position: indicators disagree or flipped (A={signal_a}, B={signal_b}) "
            "— closing SHORT immediately"
        )
        if trader.close_position(symbol=SYMBOL):
            indicator_signals['trade_active'] = False
            indicator_signals['position_side'] = None
            return 'CLOSE_SHORT'
        return 'CLOSE_SHORT_FAILED'

    # ── Unexpected state ────────────────────────────────────────────────────
    logger.warning(f"Unexpected state — trade_active={trade_active}, position_side={position_side}")
    return None

@app.route('/status', methods=['GET'])
def status():
    """Get current bot status"""
    try:
        position = None
        balance = 0
        current_price = None

        try:
            position = trader.get_position_status(symbol=SYMBOL)
        except Exception as e:
            logger.warning(f"Could not fetch position: {str(e)}")

        try:
            balance = trader.get_wallet_balance()
        except Exception as e:
            logger.warning(f"Could not fetch balance: {str(e)}")

        try:
            current_price = trader.get_current_price(symbol=SYMBOL)
        except Exception as e:
            logger.warning(f"Could not fetch price: {str(e)}")

        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'indicator_signals': indicator_signals,
            'position': position,
            'balance': balance,
            'current_price': current_price,
            'symbol': SYMBOL,
            'testnet': TESTNET
        }), 200
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/trade/open', methods=['POST'])
def manual_open_trade():
    """Manual endpoint to open a trade (for testing)"""
    try:
        data = request.get_json() or {}
        side = data.get('side', 'Buy')
        symbol = data.get('symbol', SYMBOL)

        if trader.open_position(symbol=symbol, side=side):
            indicator_signals['trade_active'] = True
            return jsonify({'status': 'success', 'action': 'position_opened'}), 200
        else:
            return jsonify({'status': 'failed', 'action': 'position_open_failed'}), 400

    except Exception as e:
        logger.error(f"Error opening trade: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/trade/close', methods=['POST'])
def manual_close_trade():
    """Manual endpoint to close a trade (for testing)"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', SYMBOL)

        if trader.close_position(symbol=symbol):
            indicator_signals['trade_active'] = False
            return jsonify({'status': 'success', 'action': 'position_closed'}), 200
        else:
            return jsonify({'status': 'failed', 'action': 'position_close_failed'}), 400

    except Exception as e:
        logger.error(f"Error closing trade: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Get current bot configuration"""
    return jsonify({
        'symbol': SYMBOL,
        'leverage': trader.leverage,
        'balance_usage': trader.balance_usage * 100,
        'stop_loss_percent': trader.stop_loss_percent * 100,
        'stop_loss_price_percent': trader.stop_loss_price_percent * 100,
        'testnet': TESTNET
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port)
