# Bybit Trading Bot

Automated trading bot that executes trades on Bybit based on TradingView webhook signals from two indicators. The bot only trades when both indicators signal the same direction (both Buy or both Sell).

## Features

- **Dual Indicator Verification**: Trades only when both indicators align
- **10x Leverage Trading**: Uses 10x leverage on all positions
- **Dynamic Position Sizing**: Utilizes 90% of available balance for every trade
- **Risk Management**: 
  - Stop loss at 24% of capital used OR 2.4% price movement
  - Automatic position closure on indicator divergence
- **Testnet Support**: Run in testnet mode before going live
- **Railway Deployment Ready**: Docker and Railway configuration included
- **Webhook Security**: API key validation for TradingView webhooks

## Project Structure

```
.
├── app.py                 # Flask webhook server & main API
├── bybit_trader.py       # Bybit API integration & trading logic
├── test_bot.py           # Test suite for local testing
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker container configuration
├── railway.json          # Railway deployment config
├── .env.example          # Environment variables template
└── README.md            # This file
```

## Installation

### 1. Prerequisites

- Python 3.11+
- Git
- (For local testing) pip
- (For deployment) Railway account

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot
```

### 3. Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
WEBHOOK_KEY=your_secure_webhook_key
SYMBOL=BTCUSDT
TESTNET=True
PORT=5000
DEBUG=False
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Local Testing

### 1. Run the Bot Locally

```bash
python app.py
```

The Flask server will start on `http://localhost:5000`

### 2. Run Test Suite

In another terminal:

```bash
python test_bot.py
```

This will:
- Test trader initialization
- Verify wallet balance retrieval
- Check price fetching
- Validate position sizing calculations
- Test leverage settings
- Simulate webhook calls (if app is running)

### 3. Manual Testing with Webhooks

While the app is running, send test webhook signals:

```bash
# Buy signal from Indicator A
curl -X POST http://localhost:5000/webhook \
  -H "X-Webhook-Key: your_webhook_key" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_a", "signal": "Buy"}'

# Buy signal from Indicator B (should trigger trade)
curl -X POST http://localhost:5000/webhook \
  -H "X-Webhook-Key: your_webhook_key" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_b", "signal": "Buy"}'

# Check bot status
curl http://localhost:5000/status

# Check configuration
curl http://localhost:5000/config

# Health check
curl http://localhost:5000/health
```

### 4. Testing Endpoints Available

- `GET /health` - Health check
- `GET /status` - Current bot status (balance, signals, position)
- `GET /config` - Bot configuration
- `POST /webhook` - Receive TradingView alerts
- `POST /trade/open` - Manual position open (testing)
- `POST /trade/close` - Manual position close (testing)

## TradingView Webhook Setup

### 1. Create Alert in TradingView

In your indicator script, add webhook calls:

```javascript
alertcondition(buySignal, title="Buy Signal", message='')
if buySignal
    request.post(url="https://your-app.railway.app/webhook", 
                 headers={"X-Webhook-Key": "your_webhook_key"}, 
                 data='{"indicator": "indicator_a", "signal": "Buy"}')

alertcondition(sellSignal, title="Sell Signal", message='')
if sellSignal
    request.post(url="https://your-app.railway.app/webhook", 
                 headers={"X-Webhook-Key": "your_webhook_key"}, 
                 data='{"indicator": "indicator_a", "signal": "Sell"}')
```

### 2. Repeat for Second Indicator

Set up similar alerts for Indicator B with `"indicator": "indicator_b"`

## Deployment on Railway

### 1. Prerequisites

- Railway account (free tier available)
- GitHub repository with your bot code

### 2. Deploy Steps

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project
4. Connect GitHub repository
5. Select this repository
6. Railway auto-detects Dockerfile and deploys
7. Add environment variables in Railway dashboard:
   - `BYBIT_API_KEY`
   - `BYBIT_API_SECRET`
   - `WEBHOOK_KEY`
   - `SYMBOL`
   - `TESTNET` (set to `False` for live trading)

### 3. Verify Deployment

```bash
# Check health
curl https://your-app.railway.app/health

# Check status
curl https://your-app.railway.app/status
```

## Trading Logic

### Buy Condition
- Indicator A signals Buy AND Indicator B signals Buy
- No active position
→ Opens a BUY position with 10x leverage using 90% balance

### Sell Condition
1. **Both Indicators Sell**: Both A and B signal Sell + Active position → Close position
2. **Indicator Divergence**: One indicator changes to Sell while other is Buy → Immediately close position (Emergency sell)

### Position Management

```
Balance: $1,000
↓
Usable (90%): $900
↓
With 10x Leverage: $9,000 position
↓
BTC Price: $45,000
↓
Position Size: 0.2 BTC

Stop Loss Triggers:
- If loss reaches 24% of capital used: CLOSE
- OR if price moves 2.4% against position: CLOSE
- Whichever happens first
```

## Risk Management Settings

All settings are configurable in `bybit_trader.py`:

```python
self.leverage = 10              # 10x leverage
self.balance_usage = 0.90       # Use 90% of balance
self.stop_loss_percent = 0.24   # 24% loss threshold
self.stop_loss_price_percent = 0.024  # 2.4% price movement
```

## API Response Examples

### Status Endpoint
```json
{
  "timestamp": "2024-04-22T15:30:00.000000",
  "indicator_signals": {
    "indicator_a": "Buy",
    "indicator_b": "Buy",
    "last_update": "2024-04-22T15:29:50.000000",
    "trade_active": true
  },
  "balance": 1000.50,
  "current_price": 45250.75,
  "symbol": "BTCUSDT",
  "testnet": true
}
```

### Config Endpoint
```json
{
  "symbol": "BTCUSDT",
  "leverage": 10,
  "balance_usage": 90,
  "stop_loss_percent": 24,
  "stop_loss_price_percent": 2.4,
  "testnet": true
}
```

## Logging

The bot logs all activities to console:

```
2024-04-22 15:30:00 - INFO - Webhook received: {"indicator": "indicator_a", "signal": "Buy"}
2024-04-22 15:30:01 - INFO - Both indicators signal BUY - Opening position
2024-04-22 15:30:02 - INFO - Opening Buy position for 0.2 BTC
2024-04-22 15:30:03 - INFO - Order placed successfully. Order ID: abc123
```

## Important Notes

⚠️ **Before Live Trading:**
1. **Test thoroughly** in testnet mode first
2. **Start with small amounts** for your first live trades
3. **Monitor position closely** - watch the logs and status endpoint
4. **Verify webhook integration** - ensure TradingView alerts reach your bot
5. **Check API keys** - ensure Bybit API has required permissions
6. **Review risk settings** - confirm leverage and stop loss thresholds match your risk tolerance

⚠️ **API Key Security:**
- Never commit `.env` file to GitHub
- Use strong webhook keys
- Restrict Bybit API keys to only required permissions (trading)
- Use testnet API keys until confident

## Troubleshooting

### No trades executing

1. Check logs for webhook errors
2. Verify webhook key matches in TradingView and app
3. Ensure both indicators are sending signals
4. Check that signals are arriving (test endpoint)

### Position not opening

1. Verify balance is sufficient
2. Check Bybit API connection
3. Review available balance in Bybit account
4. Ensure leverage setting succeeded

### Railway deployment fails

1. Check logs: `railway logs`
2. Verify environment variables are set
3. Ensure Docker builds locally: `docker build .`
4. Check for syntax errors in code

## Support

For issues or questions:
1. Check logs for error messages
2. Review test_bot.py output
3. Test webhook manually with curl
4. Check Bybit API documentation

## License

MIT License - Use at your own risk
