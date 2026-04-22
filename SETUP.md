# Trading Bot Setup Guide

## Quick Start (5 minutes)

### Step 1: Get Your Bybit API Keys

1. Go to [Bybit.com](https://www.bybit.com)
2. Login to your account
3. Go to Account → API Management
4. Create a new API key with these permissions:
   - Trading (Futures/Linear)
   - Read (Position, Wallet)
5. Copy your API Key and API Secret

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot

# Create environment file
cp .env.example .env
```

### Step 3: Configure Environment

Edit `.env` file with:
```
BYBIT_API_KEY=your_actual_api_key
BYBIT_API_SECRET=your_actual_api_secret
WEBHOOK_KEY=create_a_random_secure_key
SYMBOL=BTCUSDT
TESTNET=True
```

Generate a secure webhook key:
```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows PowerShell
[System.Convert]::ToHexString((1..32 | ForEach-Object { [byte](Get-Random -Maximum 256) }))
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Test Locally

```bash
# In terminal 1: Start the bot
python app.py

# In terminal 2: Run tests
python test_bot.py
```

You should see:
- "Flask app running on http://0.0.0.0:5000"
- Test outputs showing successful initialization

## Testing Workflow

### 1. Verify Connection to Bybit

```bash
python test_bot.py
```

Look for:
- "Wallet balance retrieved: X USDT"
- "Current price retrieved: XXXXX"

### 2. Test Webhook Locally

Start the app:
```bash
python app.py
```

In another terminal, send a test:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "X-Webhook-Key: your_webhook_key_from_env" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_a", "signal": "Buy"}'
```

### 3. Check Status

```bash
curl http://localhost:5000/status
```

Should return JSON with current balance, price, and signal status.

## Testnet vs Live Trading

### Testnet Mode (Safe for Testing)

```
TESTNET=True
BYBIT_API_KEY=your_testnet_api_key
BYBIT_API_SECRET=your_testnet_api_secret
```

- Use testnet API keys from Bybit
- Practice without real money risk
- Recommended: Test for at least 1 week

### Live Mode (Real Money)

```
TESTNET=False
BYBIT_API_KEY=your_live_api_key
BYBIT_API_SECRET=your_live_api_secret
```

**IMPORTANT:** 
1. Only switch to live AFTER successful testnet testing
2. Start with MINIMUM amount first
3. Keep 10x leverage setting
4. Monitor closely first 24 hours

## TradingView Indicator Setup

### Create Buy Alert

In your TradingView indicator script, add:

```javascript
buy_signal = /* your indicator logic */

alertcondition(buy_signal, 
    title="Indicator A Buy", 
    message="Indicator A Buy Signal")

if buy_signal
    request.post(url="https://your-bot-url.railway.app/webhook",
        headers={"X-Webhook-Key": "your_webhook_key"},
        data='{"indicator": "indicator_a", "signal": "Buy"}')
```

### Create Sell Alert

```javascript
sell_signal = /* your indicator logic */

alertcondition(sell_signal, 
    title="Indicator A Sell", 
    message="Indicator A Sell Signal")

if sell_signal
    request.post(url="https://your-bot-url.railway.app/webhook",
        headers={"X-Webhook-Key": "your_webhook_key"},
        data='{"indicator": "indicator_a", "signal": "Sell"}')
```

### Repeat for Indicator B

Use same webhook URL but change:
```
"indicator": "indicator_b"
```

## Railway Deployment (10 minutes)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial trading bot commit"
git push origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select your trading-bot repository
6. Railway auto-detects Dockerfile → auto-deploys
7. Wait 2-3 minutes for build to complete

### Step 3: Set Environment Variables

1. Click on deployment in Railway
2. Go to "Variables" tab
3. Add these variables:
   ```
   BYBIT_API_KEY=your_live_api_key
   BYBIT_API_SECRET=your_live_api_secret
   WEBHOOK_KEY=your_webhook_key
   SYMBOL=BTCUSDT
   TESTNET=False
   ```
4. Click "Deploy"

### Step 4: Get Your Webhook URL

Railway assigns a URL like: `https://trading-bot-prod.railway.app`

Use this in TradingView:
```
https://trading-bot-prod.railway.app/webhook
```

## Monitoring Your Bot

### Check Logs on Railway

```bash
# Via Railway CLI
railway logs

# Or view in Railway dashboard: Deployments → Logs
```

### Monitor Trades

Check status endpoint:
```bash
curl https://your-bot.railway.app/status
```

Response shows:
- Current balance
- Active signals from both indicators
- Position status
- Current price

### Set Up Alerts (Optional)

Add to your status monitoring:
```bash
# Check every minute
watch -n 60 'curl -s https://your-bot.railway.app/status | jq .'
```

## Risk Management Checklist

- [ ] Tested in testnet for at least 1 week
- [ ] Webhook integration verified working
- [ ] Both indicators sending signals properly
- [ ] Started with small trade amount
- [ ] Monitor logs for first 24 hours
- [ ] Verify stop loss triggers work
- [ ] Check leverage is set to 10x
- [ ] Confirm balance usage is ~90%

## Troubleshooting

### Bot not responding to webhooks

1. Check webhook URL is correct
2. Verify webhook key in TradingView matches .env
3. Check logs: `railway logs`
4. Test manually: `curl -X POST https://your-bot/webhook ...`

### No position opening

1. Check wallet balance: `curl https://your-bot/status`
2. Verify both indicators signaled same direction
3. Check Bybit account has sufficient balance
4. Review logs for API errors

### Position not closing

1. Check indicator signals diverged
2. Verify close order endpoint working
3. Check Bybit for position status
4. Review logs for close order errors

## Getting Help

1. Check logs first: `railway logs`
2. Test manually with curl
3. Verify environment variables
4. Check Bybit API status
5. Review code comments in app.py and bybit_trader.py

## Next Steps

1. Clone the repo
2. Set up .env file
3. Run test_bot.py
4. Test webhooks locally
5. Deploy to Railway
6. Set up TradingView alerts
7. Monitor first trades carefully
8. Scale up slowly

Good luck with your trading bot!
