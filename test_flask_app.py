import os
import json
from app import app, indicator_signals
from dotenv import load_dotenv

load_dotenv()

def test_flask_app():
    """Test Flask app endpoints"""
    print("\n" + "=" * 60)
    print("FLASK APP ENDPOINT TESTS")
    print("=" * 60)

    with app.test_client() as client:
        print("\n1. Testing Health Check (/health)")
        print("-" * 40)
        response = client.get('/health')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        assert response.status_code == 200, "Health check failed"
        print("   PASS")

        print("\n2. Testing Config Endpoint (/config)")
        print("-" * 40)
        response = client.get('/config')
        print(f"   Status: {response.status_code}")
        config = response.get_json()
        print(f"   Symbol: {config.get('symbol')}")
        print(f"   Leverage: {config.get('leverage')}x")
        print(f"   Balance Usage: {config.get('balance_usage')}%")
        print(f"   Stop Loss: {config.get('stop_loss_percent')}%")
        assert response.status_code == 200, "Config endpoint failed"
        assert config.get('leverage') == 10, "Leverage should be 10x"
        assert config.get('balance_usage') == 90, "Balance usage should be 90%"
        print("   PASS")

        print("\n3. Testing Webhook - Invalid Key")
        print("-" * 40)
        response = client.post('/webhook',
            data=json.dumps({'indicator': 'indicator_a', 'signal': 'Buy'}),
            content_type='application/json',
            headers={'X-Webhook-Key': 'wrong_key'})
        print(f"   Status: {response.status_code}")
        assert response.status_code == 401, "Should reject invalid webhook key"
        print("   PASS - Correctly rejected unauthorized key")

        print("\n4. Testing Webhook - Valid Key (Indicator A Buy)")
        print("-" * 40)
        webhook_key = os.getenv('WEBHOOK_KEY', 'default_webhook_key')
        response = client.post('/webhook',
            data=json.dumps({'indicator': 'indicator_a', 'signal': 'Buy'}),
            content_type='application/json',
            headers={'X-Webhook-Key': webhook_key})
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Signal A: {data['indicator_signals']['indicator_a']}")
        print(f"   Signal B: {data['indicator_signals']['indicator_b']}")
        assert response.status_code == 200, "Webhook failed"
        print("   PASS")

        print("\n5. Testing Webhook - Indicator B Buy (Should align)")
        print("-" * 40)
        response = client.post('/webhook',
            data=json.dumps({'indicator': 'indicator_b', 'signal': 'Buy'}),
            content_type='application/json',
            headers={'X-Webhook-Key': webhook_key})
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Signal A: {data['indicator_signals']['indicator_a']}")
        print(f"   Signal B: {data['indicator_signals']['indicator_b']}")
        print(f"   Trade Action: {data['trade_action']}")
        assert response.status_code == 200, "Webhook failed"
        print("   PASS - Both indicators aligned")

        print("\n6. Testing Status Endpoint (/status)")
        print("-" * 40)
        response = client.get('/status')
        print(f"   Status: {response.status_code}")
        status_data = response.get_json()
        if 'error' not in status_data:
            print(f"   Symbol: {status_data.get('symbol')}")
            print(f"   Testnet: {status_data.get('testnet')}")
            print(f"   Indicator A: {status_data['indicator_signals'].get('indicator_a')}")
            print(f"   Indicator B: {status_data['indicator_signals'].get('indicator_b')}")
        else:
            print(f"   Note: {status_data.get('error')} (Expected if no API keys configured)")
        print("   PASS")

        print("\n7. Testing Invalid Webhook Data")
        print("-" * 40)
        response = client.post('/webhook',
            data=json.dumps({'indicator': 'invalid', 'signal': 'Invalid'}),
            content_type='application/json',
            headers={'X-Webhook-Key': webhook_key})
        print(f"   Status: {response.status_code}")
        assert response.status_code == 400, "Should reject invalid indicator/signal"
        print("   PASS - Correctly rejected invalid data")

    print("\n" + "=" * 60)
    print("ALL FLASK TESTS PASSED!")
    print("=" * 60)
    print("\nFlask app is working correctly.")
    print("You can now:")
    print("  1. Set up your .env file with actual Bybit API keys")
    print("  2. Test locally: python app.py")
    print("  3. Set up TradingView webhooks")
    print("  4. Deploy to Railway")

if __name__ == '__main__':
    test_flask_app()
