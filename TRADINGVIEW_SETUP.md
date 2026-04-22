# TradingView Webhook Setup for Your Bot

**Bot URL:** `https://bottk.up.railway.app`  
**Webhook Key:** `BotTK`  
**Status:** ✓ Live and Ready

---

## Quick Copy-Paste Webhook Messages

### For Indicator A - BUY Signal
```json
{"indicator": "indicator_a", "signal": "Buy"}
```

### For Indicator A - SELL Signal
```json
{"indicator": "indicator_a", "signal": "Sell"}
```

### For Indicator B - BUY Signal
```json
{"indicator": "indicator_b", "signal": "Buy"}
```

### For Indicator B - SELL Signal
```json
{"indicator": "indicator_b", "signal": "Sell"}
```

---

## Complete Pine Script Code for TradingView

### INDICATOR A - Full Script

```pinescript
//@version=5
indicator("Trading Bot - Indicator A", overlay=true)

// Your indicator logic here - Replace with your actual indicator
buyCondition = ta.crossover(ta.sma(close, 9), ta.sma(close, 21))
sellCondition = ta.crossunder(ta.sma(close, 9), ta.sma(close, 21))

// Alert for Buy
alertcondition(buyCondition, title="Indicator A Buy", message="")
if buyCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=array.new<string>("X-Webhook-Key", "BotTK", "Content-Type", "application/json"),
        data='{"indicator": "indicator_a", "signal": "Buy"}')

// Alert for Sell
alertcondition(sellCondition, title="Indicator A Sell", message="")
if sellCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=array.new<string>("X-Webhook-Key", "BotTK", "Content-Type", "application/json"),
        data='{"indicator": "indicator_a", "signal": "Sell"}')

// Plotting
plot(ta.sma(close, 9), color=color.blue, title="SMA 9")
plot(ta.sma(close, 21), color=color.red, title="SMA 21")
plotshape(buyCondition, style=shape.arrowup, location=location.belowbar, color=color.green, size=size.small, title="Buy")
plotshape(sellCondition, style=shape.arrowdown, location=location.abovebar, color=color.red, size=size.small, title="Sell")
```

### INDICATOR B - Full Script

```pinescript
//@version=5
indicator("Trading Bot - Indicator B", overlay=true)

// Your indicator logic here - Replace with your actual indicator
buyCondition = ta.crossover(ta.rsi(close, 14), 30)
sellCondition = ta.crossunder(ta.rsi(close, 14), 70)

// Alert for Buy
alertcondition(buyCondition, title="Indicator B Buy", message="")
if buyCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=array.new<string>("X-Webhook-Key", "BotTK", "Content-Type", "application/json"),
        data='{"indicator": "indicator_b", "signal": "Buy"}')

// Alert for Sell
alertcondition(sellCondition, title="Indicator B Sell", message="")
if sellCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=array.new<string>("X-Webhook-Key", "BotTK", "Content-Type", "application/json"),
        data='{"indicator": "indicator_b", "signal": "Sell"}')

// Plotting
rsi = ta.rsi(close, 14)
plot(rsi, color=color.purple, title="RSI")
hline(70, "Overbought", color=color.red)
hline(30, "Oversold", color=color.green)
hline(50, "Middle", color=color.gray)
plotshape(buyCondition, style=shape.arrowup, location=location.belowbar, color=color.green, size=size.small, title="Buy")
plotshape(sellCondition, style=shape.arrowdown, location=location.abovebar, color=color.red, size=size.small, title="Sell")
```

---

## How to Set Up in TradingView

### Step 1: Add Your Indicator A
1. Go to TradingView chart
2. Click "Open Editor" (Pine Script icon)
3. Create New → Create a new indicator
4. Copy the **INDICATOR A** code above
5. Click "Save" → Give it a name (e.g., "My Indicator A")
6. Click "Add to Chart"

### Step 2: Create Alert for Indicator A Buy
1. Click "Create Alert" (Bell icon)
2. Select your "My Indicator A" script
3. Select condition: "Indicator A Buy"
4. **Webhook URL:** `https://bottk.up.railway.app/webhook`
5. **Headers:**
   ```
   X-Webhook-Key: BotTK
   Content-Type: application/json
   ```
6. **Message:**
   ```json
   {"indicator": "indicator_a", "signal": "Buy"}
   ```
7. Click "Create Alert"

### Step 3: Create Alert for Indicator A Sell
1. Click "Create Alert" again
2. Same script "My Indicator A"
3. Select condition: "Indicator A Sell"
4. **Webhook URL:** `https://bottk.up.railway.app/webhook`
5. **Headers:**
   ```
   X-Webhook-Key: BotTK
   Content-Type: application/json
   ```
6. **Message:**
   ```json
   {"indicator": "indicator_a", "signal": "Sell"}
   ```
7. Click "Create Alert"

### Step 4: Add Your Indicator B
1. Repeat Step 1 with **INDICATOR B** code
2. Name it "My Indicator B"

### Step 5: Create Alert for Indicator B Buy
1. Same as Step 2 but:
2. Select "My Indicator B" script
3. Select condition: "Indicator B Buy"
4. **Message:**
   ```json
   {"indicator": "indicator_b", "signal": "Buy"}
   ```

### Step 6: Create Alert for Indicator B Sell
1. Same as Step 3 but:
2. Select "My Indicator B" script
3. Select condition: "Indicator B Sell"
4. **Message:**
   ```json
   {"indicator": "indicator_b", "signal": "Sell"}
   ```

---

## Alert Configuration Summary

| Alert | Indicator | Condition | Message |
|-------|-----------|-----------|---------|
| 1 | A | Buy | `{"indicator": "indicator_a", "signal": "Buy"}` |
| 2 | A | Sell | `{"indicator": "indicator_a", "signal": "Sell"}` |
| 3 | B | Buy | `{"indicator": "indicator_b", "signal": "Buy"}` |
| 4 | B | Sell | `{"indicator": "indicator_b", "signal": "Sell"}` |

**All alerts use:**
- **URL:** `https://bottk.up.railway.app/webhook`
- **Header:** `X-Webhook-Key: BotTK`
- **Content-Type:** `application/json`

---

## Trading Bot Behavior

Your bot will trade based on **BOTH indicators aligning**:

### Buy Trade Opens When:
- **Indicator A** sends: `Buy`
- **AND Indicator B** sends: `Buy`
- Bot opens **BUY position** with:
  - 10x leverage
  - 90% of balance
  - Stop loss at 24% loss OR 2.4% price move

### Sell/Close Trade When:
1. **Both indicators sell:** Indicator A `Sell` + Indicator B `Sell` → Close position
2. **Indicators diverge:** One says Buy, other says Sell → **Emergency Close** (protects capital)
3. **Stop loss triggered:** 24% loss reached OR 2.4% price movement

---

## Testing Your Setup

### Test Webhook Manually
```bash
# Test Indicator A Buy
curl -X POST https://bottk.up.railway.app/webhook \
  -H "X-Webhook-Key: BotTK" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_a", "signal": "Buy"}'

# Test Indicator B Buy (should trigger trade)
curl -X POST https://bottk.up.railway.app/webhook \
  -H "X-Webhook-Key: BotTK" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_b", "signal": "Buy"}'

# Check bot status
curl https://bottk.up.railway.app/status
```

### Monitor Bot Status
```bash
# Check current balance, signals, and position
curl https://bottk.up.railway.app/status | jq '.'
```

Response will show:
```json
{
  "indicator_signals": {
    "indicator_a": "Buy",
    "indicator_b": "Buy",
    "trade_active": true
  },
  "balance": 1000.50,
  "current_price": 45250.75
}
```

---

## Important Notes

⚠️ **Before Going Live:**
1. Verify both indicators are sending signals correctly
2. Test each webhook individually
3. Confirm alerts are firing in TradingView
4. Monitor the first few trades carefully
5. Check bot logs: `railway logs --service trading-bot`

⚠️ **Alert Settings in TradingView:**
- Set alerts to **"Once Per Bar Close"** (not "Every Tick")
- This prevents multiple signals from same candle
- Recommended: 1-hour or higher timeframe

⚠️ **Webhook Key:**
- Keep `BotTK` secure
- Don't share publicly
- If compromised, change in Railway dashboard

---

## Quick Reference Cheat Sheet

```
Bot URL: https://bottk.up.railway.app
Webhook Key: BotTK

Indicator A Buy:   {"indicator": "indicator_a", "signal": "Buy"}
Indicator A Sell:  {"indicator": "indicator_a", "signal": "Sell"}
Indicator B Buy:   {"indicator": "indicator_b", "signal": "Buy"}
Indicator B Sell:  {"indicator": "indicator_b", "signal": "Sell"}

All webhooks POST to: https://bottk.up.railway.app/webhook
All webhooks need header: X-Webhook-Key: BotTK
```

---

## Troubleshooting

### Webhook not triggering
- Verify URL is exactly: `https://bottk.up.railway.app/webhook`
- Check header key is: `X-Webhook-Key: BotTK` (case-sensitive)
- Verify message JSON is valid
- Check TradingView alert is enabled
- View bot logs: `railway logs`

### Bot not opening trades
- Check both indicators sent signals
- Verify signals are in same direction
- Check balance in Bybit account
- View status: `curl https://bottk.up.railway.app/status`

### Wrong alerts firing
- Confirm indicator conditions are correct
- Test each alert individually
- Check alert notifications in TradingView
- Review bot logs for webhook receipt

---

You're all set! Your bot is live and ready to receive webhook signals. 🚀
