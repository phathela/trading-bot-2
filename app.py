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
    'trade_active': False
}

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
    """Process signals from both indicators and execute trades"""
    signal_a = indicator_signals['indicator_a']
    signal_b = indicator_signals['indicator_b']

    if signal_a is None or signal_b is None:
        logger.info("Waiting for both indicators to signal...")
        return None

    if signal_a != signal_b:
        logger.info(f"Indicators not aligned: A={signal_a}, B={signal_b}")
        return None

    current_action = None

    if signal_a == signal_b == 'Buy' and not indicator_signals['trade_active']:
        logger.info("Both indicators signal BUY - Opening position")
        current_action = 'BUY'
        if trader.open_position(symbol=SYMBOL, side='Buy'):
            indicator_signals['trade_active'] = True
        return current_action

    elif signal_a == signal_b == 'Sell' and indicator_signals['trade_active']:
        logger.info("Both indicators signal SELL - Closing position")
        current_action = 'SELL'
        if trader.close_position(symbol=SYMBOL):
            indicator_signals['trade_active'] = False
        return current_action

    elif signal_a == 'Sell' and indicator_signals['trade_active'] and (signal_a != signal_b):
        logger.info("One indicator changed to SELL - Closing position immediately")
        current_action = 'EMERGENCY_SELL'
        if trader.close_position(symbol=SYMBOL):
            indicator_signals['trade_active'] = False
        return current_action

    return current_action

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
