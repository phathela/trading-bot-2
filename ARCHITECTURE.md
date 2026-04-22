# Trading Bot Architecture

## System Overview

```
TradingView Indicators
      |
      | (Webhook POST)
      v
Flask API Server
      |
      +-- Webhook Handler: Receives indicator signals
      |
      +-- Signal Processor: Monitors dual indicator alignment
      |
      +-- Trading Engine: Executes orders
      |
      v
Bybit API (10x Leverage Linear Trading)
      |
      v
Live Trading Account
```

## Components

### 1. Flask Application (`app.py`)

**Purpose:** Receives webhooks from TradingView and manages trade execution

**Key Endpoints:**
- `POST /webhook` - Receives indicator signals from TradingView
- `GET /status` - Returns current bot state
- `GET /config` - Returns bot configuration
- `POST /trade/open` - Manual trade opening (testing)
- `POST /trade/close` - Manual trade closing (testing)
- `GET /health` - Health check endpoint

**Signal Processing Logic:**
```
Indicator A Signal + Indicator B Signal
       |
       v
  Same Direction?
       |
    +--+--+
    |     |
   YES    NO
    |     |
    |    Divergence = Close Position
    |
    v
Buy (Both Buy)  OR  Sell (Both Sell)
    |
    v
Execute Order with 10x Leverage
```

### 2. Trading Engine (`bybit_trader.py`)

**Purpose:** Interfaces with Bybit API and executes trades

**Key Classes:** `BybitTrader`

**Core Methods:**

```python
# Position Management
open_position(side='Buy')      # Opens a position with 90% balance at 10x leverage
close_position()               # Closes active position with market order
check_stop_loss()              # Monitors stop loss conditions

# Market Data
get_current_price(symbol)      # Fetches latest price
get_wallet_balance()           # Gets available balance
get_position_status()          # Retrieves active positions

# Configuration
set_leverage(leverage=10)      # Sets trading leverage
calculate_position_size()      # Calculates position size based on balance
```

**Risk Management:**
- Leverage: 10x fixed
- Balance Usage: 90% of wallet
- Stop Loss: Triggered at 24% loss OR 2.4% price movement
- Position Type: Linear (Perpetual Futures)

## Data Flow

### Trade Opening Flow

```
1. TradingView sends: {"indicator": "indicator_a", "signal": "Buy"}
   |
2. Flask webhook handler receives and validates
   |
3. Stores signal_a = Buy
   |
4. Waits for indicator_b signal
   |
5. When signal_b = Buy received:
   |
6. Trigger process_trade_signals()
   |
7. Both signals are Buy -> Open Position
   |
8. Get wallet balance (e.g., $1,000)
   |
9. Calculate usable amount: $1,000 * 0.90 = $900
   |
10. Apply 10x leverage: $900 * 10 = $9,000
   |
11. Get current BTC price: $45,000
   |
12. Calculate position size: $9,000 / $45,000 = 0.2 BTC
   |
13. Send Buy market order to Bybit for 0.2 BTC at 10x leverage
   |
14. Store position details (price, size, time, etc.)
   |
15. Start monitoring for stop loss
```

### Trade Closing Flow

```
Condition 1: Both Indicators Signal Sell
   |
   v
Trigger close_position()
   |
   v
Send Sell market order (opposite of entry)
   |
   v
Calculate P&L
   |
   v
Reset position tracking

---

Condition 2: Indicators Diverge (One Sells, One Buys)
   |
   v
Emergency Close (Reduce Risk)
   |
   v
Send Sell market order immediately
   |
   v
Calculate P&L
   |
   v
Reset position tracking

---

Condition 3: Stop Loss Triggered
   |
   v
24% loss reached OR 2.4% price movement
   |
   v
Auto close position
   |
   v
Prevent further losses
```

## Configuration Parameters

All configurable in environment variables:

```
BYBIT_API_KEY          # Bybit API authentication
BYBIT_API_SECRET       # Bybit API authentication
WEBHOOK_KEY            # Webhook security key
SYMBOL                 # Trading pair (default: BTCUSDT)
TESTNET                # true = testnet, false = live trading
PORT                   # Flask server port
DEBUG                  # Flask debug mode
```

Fixed in code:
```python
leverage = 10
balance_usage = 0.90       # 90%
stop_loss_percent = 0.24   # 24% capital loss
stop_loss_price_percent = 0.024  # 2.4% price movement
```

## State Management

### Indicator Signals State
```python
indicator_signals = {
    'indicator_a': None,        # Buy, Sell, or None
    'indicator_b': None,        # Buy, Sell, or None
    'last_update': timestamp,   # When last signal received
    'trade_active': bool        # Is position currently open?
}
```

### Position State
```python
position = {
    'symbol': 'BTCUSDT',
    'side': 'Buy',                  # Buy or Sell
    'qty': 0.2,                    # Position size in BTC
    'order_id': 'xxx',             # Bybit order ID
    'entry_price': 45000.00,       # Entry price
    'timestamp': 'ISO-8601'        # When position opened
}
```

## Error Handling

**API Errors:**
- Invalid API keys → Logged and skipped
- Network issues → Timeout and retry
- Invalid parameters → Logged and rejected

**Trade Errors:**
- Insufficient balance → Position not opened
- Invalid position size → Logged and skipped
- Order rejection → Error logged, no trade executed

**Webhook Errors:**
- Invalid webhook key → 401 Unauthorized
- Missing fields → 400 Bad Request
- Invalid signal → 400 Bad Request

## Deployment Architecture

### Local Development
```
Your Computer
    |
    +-- Python 3.11
    +-- Flask dev server (http://localhost:5000)
    +-- Bybit Testnet API
    +-- TradingView Webhook (via ngrok or tunnel)
```

### Railway Production
```
Railway Container
    |
    +-- Docker Image (Python 3.11)
    +-- Gunicorn WSGI Server
    +-- Environment Variables (Secrets)
    +-- Bybit Live API
    +-- Public HTTPS URL
         |
         v
    TradingView Webhooks
```

## Security Considerations

1. **API Keys:**
   - Never commit .env to Git
   - Use environment variables
   - Restrict Bybit API key permissions to: Trading, Read-only

2. **Webhook Security:**
   - X-Webhook-Key validation on every request
   - Reject unauthorized requests (401)
   - Log all webhook attempts

3. **Position Protection:**
   - Stop loss prevents catastrophic losses
   - Never trade without stop loss configured
   - Emergency close on indicator divergence

4. **Rate Limiting:**
   - Bybit API rate limits: 10 orders/second
   - TradingView webhooks: Throttled to prevent spam
   - Response caching where appropriate

## Monitoring & Logging

**Log Levels:**
- INFO: Trade executions, signals, balance updates
- WARNING: Stop loss triggers, order failures
- ERROR: API errors, connection issues

**Monitoring Points:**
- Webhook reception
- Signal alignment
- Order placement
- Order execution
- Position status
- P&L calculation

**Health Checks:**
- `/health` endpoint for uptime monitoring
- `/status` endpoint for detailed state
- Railway logs for error tracking

## Testing Strategy

1. **Unit Tests:** Trader initialization, calculations
2. **Integration Tests:** Flask endpoints, webhook flow
3. **Manual Tests:** Live API connection, order execution
4. **Smoke Tests:** Testnet trading, position management

**Test Files:**
- `test_bot.py` - Full trading logic tests
- `test_flask_app.py` - Flask endpoint tests

## Performance Considerations

1. **Response Time:**
   - Webhook processing: <1 second
   - Order placement: 1-2 seconds
   - Status checks: <500ms

2. **Concurrency:**
   - Single worker (Gunicorn)
   - One position at a time
   - Sequential order processing

3. **Resource Usage:**
   - CPU: Minimal (webhook processing)
   - Memory: ~50-100MB
   - Network: Only during order execution

## Future Enhancements

Possible improvements (not in v1):
1. Multiple symbol support
2. Indicator weighting (more confidence in one vs other)
3. Time-based filters (trading hours only)
4. Position size scaling
5. Trailing stop loss
6. Discord/Telegram notifications
7. Database logging for trades
8. Advanced risk metrics
9. Backtesting engine
10. Portfolio management

## Files Structure

```
trading-bot/
├── app.py                 # Flask application
├── bybit_trader.py       # Trading engine
├── test_bot.py           # Main test suite
├── test_flask_app.py     # Flask endpoint tests
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition
├── railway.json          # Railway config
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # User documentation
├── SETUP.md              # Setup instructions
└── ARCHITECTURE.md       # This file
```

## Version History

**v1.0.0 (Initial Release)**
- Dual indicator trading
- 10x leverage
- 90% balance usage
- 24% stop loss
- Webhook receiver
- Testnet support
- Railway deployment ready
