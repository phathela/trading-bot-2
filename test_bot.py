import os
import json
import time
import requests
from dotenv import load_dotenv
from bybit_trader import BybitTrader

load_dotenv()

API_KEY = os.getenv('BYBIT_API_KEY', 'test_key')
API_SECRET = os.getenv('BYBIT_API_SECRET', 'test_secret')
TESTNET = True

def test_trader_initialization():
    """Test trader initialization"""
    print("\n=== Testing Trader Initialization ===")
    try:
        trader = BybitTrader(api_key=API_KEY, api_secret=API_SECRET, testnet=TESTNET)
        print("✓ Trader initialized successfully")
        print(f"  Leverage: {trader.leverage}x")
        print(f"  Balance usage: {trader.balance_usage * 100}%")
        print(f"  Stop loss: {trader.stop_loss_percent * 100}% or {trader.stop_loss_price_percent * 100}% price movement")
        return trader
    except Exception as e:
        print(f"✗ Error initializing trader: {str(e)}")
        return None

def test_wallet_balance(trader):
    """Test wallet balance retrieval"""
    print("\n=== Testing Wallet Balance ===")
    try:
        balance = trader.get_wallet_balance()
        print(f"✓ Balance retrieved: {balance} USDT")
        return balance
    except Exception as e:
        print(f"✗ Error getting balance: {str(e)}")
        return 0

def test_current_price(trader, symbol="BTCUSDT"):
    """Test current price retrieval"""
    print(f"\n=== Testing Current Price for {symbol} ===")
    try:
        price = trader.get_current_price(symbol)
        if price:
            print(f"✓ Current price retrieved: {price}")
            return price
        else:
            print("✗ Failed to retrieve price")
            return None
    except Exception as e:
        print(f"✗ Error getting price: {str(e)}")
        return None

def test_position_size_calculation(trader, balance, symbol="BTCUSDT"):
    """Test position size calculation"""
    print(f"\n=== Testing Position Size Calculation ===")
    try:
        pos_size = trader.calculate_position_size(balance, symbol)
        if pos_size > 0:
            print(f"✓ Position size calculated: {pos_size} {symbol}")
            return pos_size
        else:
            print("✗ Invalid position size")
            return 0
    except Exception as e:
        print(f"✗ Error calculating position size: {str(e)}")
        return 0

def test_leverage_setting(trader, symbol="BTCUSDT"):
    """Test leverage setting"""
    print(f"\n=== Testing Leverage Setting ===")
    try:
        result = trader.set_leverage(symbol=symbol, leverage=10)
        if result:
            print("✓ Leverage set successfully to 10x")
            return True
        else:
            print("✗ Failed to set leverage")
            return False
    except Exception as e:
        print(f"✗ Error setting leverage: {str(e)}")
        return False

def test_webhook_simulation():
    """Simulate webhook calls to the Flask app"""
    print("\n=== Testing Webhook Simulation ===")

    base_url = "http://localhost:5000"
    webhook_key = os.getenv('WEBHOOK_KEY', 'default_webhook_key')

    headers = {
        'X-Webhook-Key': webhook_key,
        'Content-Type': 'application/json'
    }

    tests = [
        {'indicator': 'indicator_a', 'signal': 'Buy'},
        {'indicator': 'indicator_b', 'signal': 'Buy'},
        {'indicator': 'indicator_a', 'signal': 'Sell'},
        {'indicator': 'indicator_b', 'signal': 'Sell'},
    ]

    for test_data in tests:
        try:
            response = requests.post(
                f"{base_url}/webhook",
                headers=headers,
                json=test_data,
                timeout=5
            )
            print(f"✓ Webhook {test_data}: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("! Flask app not running on localhost:5000")
            print("  Start the app with: python app.py")
            return False
        except Exception as e:
            print(f"✗ Error sending webhook: {str(e)}")
            return False

    return True

def test_status_endpoint():
    """Test status endpoint"""
    print("\n=== Testing Status Endpoint ===")
    base_url = "http://localhost:5000"

    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print("✓ Status endpoint working")
            print(f"  Balance: {status_data.get('balance')} USDT")
            print(f"  Current Price: {status_data.get('current_price')}")
            print(f"  Signals: A={status_data.get('indicator_signals', {}).get('indicator_a')}, B={status_data.get('indicator_signals', {}).get('indicator_b')}")
            return True
        else:
            print(f"✗ Status endpoint returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("! Flask app not running on localhost:5000")
        return False
    except Exception as e:
        print(f"✗ Error testing status endpoint: {str(e)}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    base_url = "http://localhost:5000"

    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("! Flask app not running on localhost:5000")
        return False
    except Exception as e:
        print(f"✗ Error in health check: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("TRADING BOT TEST SUITE")
    print("=" * 50)

    trader = test_trader_initialization()
    if not trader:
        print("\n✗ Cannot proceed without trader initialization")
        return

    balance = test_wallet_balance(trader)
    price = test_current_price(trader)

    if balance > 0 and price:
        test_position_size_calculation(trader, balance)
        test_leverage_setting(trader)

    print("\n" + "=" * 50)
    print("WEBHOOK & API TESTS")
    print("=" * 50)
    print("\nMake sure Flask app is running with: python app.py")
    print("Then run this again to test webhooks and endpoints\n")

    test_health_check()
    test_status_endpoint()

    print("\n" + "=" * 50)
    print("TEST SUITE COMPLETE")
    print("=" * 50)

if __name__ == '__main__':
    run_all_tests()
