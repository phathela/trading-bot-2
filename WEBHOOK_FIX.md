# Fix: 401 Unauthorized Webhook Error

Your bot is working correctly. The 401 error means the `X-Webhook-Key: BotTK` header is not being sent.

---

## ✓ Working Test (Proves Bot is Fine)

```bash
curl -X POST https://bottk.up.railway.app/webhook \
  -H "X-Webhook-Key: BotTK" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_a", "signal": "Buy"}'

# Returns 200 OK ✓
```

---

## 🔧 Fix Option 1: Correct Pine Script (RECOMMENDED)

The issue is likely in how TradingView is sending the headers. Use this corrected Pine Script that properly formats the headers array:

### INDICATOR A - Fixed Script

```pinescript
//@version=5
indicator("Trading Bot - Indicator A", overlay=true)

// Your indicator logic
buyCondition = ta.crossover(ta.sma(close, 9), ta.sma(close, 21))
sellCondition = ta.crossunder(ta.sma(close, 9), ta.sma(close, 21))

// Buy Signal
alertcondition(buyCondition, title="Indicator A Buy", message="")
if buyCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=map.new<string, string>()
            .put("X-Webhook-Key", "BotTK")
            .put("Content-Type", "application/json"),
        data='{"indicator": "indicator_a", "signal": "Buy"}')

// Sell Signal
alertcondition(sellCondition, title="Indicator A Sell", message="")
if sellCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=map.new<string, string>()
            .put("X-Webhook-Key", "BotTK")
            .put("Content-Type", "application/json"),
        data='{"indicator": "indicator_a", "signal": "Sell"}')

// Plotting
plot(ta.sma(close, 9), color=color.blue, title="SMA 9")
plot(ta.sma(close, 21), color=color.red, title="SMA 21")
plotshape(buyCondition, style=shape.arrowup, location=location.belowbar, color=color.green, size=size.small)
plotshape(sellCondition, style=shape.arrowdown, location=location.abovebar, color=color.red, size=size.small)
```

### INDICATOR B - Fixed Script

```pinescript
//@version=5
indicator("Trading Bot - Indicator B", overlay=true)

// Your indicator logic
buyCondition = ta.crossover(ta.rsi(close, 14), 30)
sellCondition = ta.crossunder(ta.rsi(close, 14), 70)

// Buy Signal
alertcondition(buyCondition, title="Indicator B Buy", message="")
if buyCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=map.new<string, string>()
            .put("X-Webhook-Key", "BotTK")
            .put("Content-Type", "application/json"),
        data='{"indicator": "indicator_b", "signal": "Buy"}')

// Sell Signal
alertcondition(sellCondition, title="Indicator B Sell", message="")
if sellCondition
    request.post(url="https://bottk.up.railway.app/webhook",
        headers=map.new<string, string>()
            .put("X-Webhook-Key", "BotTK")
            .put("Content-Type", "application/json"),
        data='{"indicator": "indicator_b", "signal": "Sell"}')

// Plotting
rsi = ta.rsi(close, 14)
plot(rsi, color=color.purple, title="RSI")
hline(70, "Overbought", color=color.red)
hline(30, "Oversold", color=color.green)
hline(50, "Middle", color=color.gray)
plotshape(buyCondition, style=shape.arrowup, location=location.belowbar, color=color.green, size=size.small)
plotshape(sellCondition, style=shape.arrowdown, location=location.abovebar, color=color.red, size=size.small)
```

**Key change:** Using `map.new<string, string>()` instead of `array.new<string>()` for headers.

---

## 🔧 Fix Option 2: Include Key in URL (Alternative)

If Option 1 doesn't work, add the key as a URL parameter:

```pinescript
//@version=5
indicator("Trading Bot - Indicator A", overlay=true)

buyCondition = ta.crossover(ta.sma(close, 9), ta.sma(close, 21))
sellCondition = ta.crossunder(ta.sma(close, 9), ta.sma(close, 21))

if buyCondition
    request.post(url="https://bottk.up.railway.app/webhook?key=BotTK",
        headers=map.new<string, string>()
            .put("Content-Type", "application/json"),
        data='{"indicator": "indicator_a", "signal": "Buy"}')

if sellCondition
    request.post(url="https://bottk.up.railway.app/webhook?key=BotTK",
        headers=map.new<string, string>()
            .put("Content-Type", "application/json"),
        data='{"indicator": "indicator_a", "signal": "Sell"}')

// Rest of code...
```

Then update your bot to accept key from URL too. Let me know if you need this.

---

## 📝 Steps to Apply Fix

1. **Delete** your current Indicator A script from TradingView
2. **Copy** the Fixed Script (Option 1) above
3. **Replace** the old code with the new code
4. **Save** and **Add to Chart**
5. **Create new alerts** with the updated script
6. **Repeat** for Indicator B

---

## ✅ Verify It's Working

After updating, send a test:

```bash
# This should now work from your indicator
curl -X POST https://bottk.up.railway.app/webhook \
  -H "X-Webhook-Key: BotTK" \
  -H "Content-Type: application/json" \
  -d '{"indicator": "indicator_a", "signal": "Buy"}'
```

---

## 🧪 Debug - Check Bot Logs

To see what TradingView is actually sending:

```bash
railway logs --service trading-bot
```

Look for lines like:
```
2026-04-22 20:00:00 - WARNING - Unauthorized webhook attempt with key: None
```

This tells you if the key is being sent or not.

---

## If Still Getting 401

Try these troubleshooting steps:

1. **Check the header format** - Make sure it's exactly: `X-Webhook-Key` (case-sensitive)

2. **Test manually first:**
   ```bash
   curl -X POST https://bottk.up.railway.app/webhook \
     -H "X-Webhook-Key: BotTK" \
     -H "Content-Type: application/json" \
     -d '{"indicator": "indicator_a", "signal": "Buy"}'
   ```
   If this returns 200 OK, your bot is fine.

3. **Verify TradingView Pine Script** - Make sure the `request.post()` is in the correct scope

4. **Check Chart Permissions** - Make sure your chart allows external connections

5. **View Bot Logs** - This will show exactly what's being received

---

## Summary

| Step | What to Do |
|------|-----------|
| 1 | Replace Indicator A with Fixed Script above |
| 2 | Replace Indicator B with Fixed Script above |
| 3 | Create new alerts with updated scripts |
| 4 | Delete old alerts |
| 5 | Test with curl first |
| 6 | Monitor bot logs |

The key difference is using `map.new()` instead of `array.new()` for proper header formatting.

**Try Option 1 first - it should fix your 401 error!** 🔧
