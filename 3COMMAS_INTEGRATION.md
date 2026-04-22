# 3Commas Integration Guide

Your indicators are already perfectly configured for 3Commas. **No script changes needed!**

Simply change the webhook URL to point to your trading bot instead.

---

## Current Setup

Your indicator is sending to:
```
https://api.3commas.io/signal_bots/webhooks
```

Your bot now has a **3Commas-compatible endpoint** that accepts the same format.

---

## 🔄 Switch to Your Bot (3 Steps)

### Step 1: Update Webhook URL

Change the webhook URL in your indicator from:
```
https://api.3commas.io/signal_bots/webhooks
```

To:
```
https://bottk.up.railway.app/webhook/3commas
```

### Step 2: Keep Everything Else the Same

Your JSON payload stays EXACTLY the same:
```json
{
  "secret": "eyJhbGciOiJIUzI1NiJ9.eyJzaWduYWxzX3NvdXJjZV9pZCI6NTc4Mzl9.F2p3voUTipO8hY-JqZezt0qJyEX9lr6JQqr-zc1fbyw",
  "max_lag": "300",
  "timestamp": "{{timenow}}",
  "trigger_price": "{{close}}",
  "tv_exchange": "{{exchange}}",
  "tv_instrument": "{{ticker}}",
  "action": "enter_short",
  "bot_uuid": "d97dabb2-b1c3-4596-baa1-ae8c5f23ebb6"
}
```

### Step 3: Done!

Your indicator will now send signals directly to your trading bot.

---

## Action Mapping

Your bot automatically converts 3Commas actions to trading signals:

| 3Commas Action | Trading Bot Signal | Bybit Action |
|---|---|---|
| `enter_long` | Buy | Open BUY position (10x leverage) |
| `enter_short` | Sell | Close position / Open SHORT |
| `close_long` | Sell | Close position |
| `close_short` | Buy | Open position |

---

## How It Works

Your bot receives:
```json
{"action": "enter_long"}
```

Converts to:
```json
{"indicator": "indicator_a", "signal": "Buy"}
```

Then executes the trade on Bybit with 10x leverage and 90% balance usage.

---

## Testing the Integration

### Test 1: Send enter_long (Buy)
```bash
curl -X POST https://bottk.up.railway.app/webhook/3commas \
  -H "Content-Type: application/json" \
  -d '{
    "action": "enter_long",
    "timestamp": "2026-04-22T20:00:00",
    "trigger_price": "45000",
    "tv_exchange": "BINANCE",
    "tv_instrument": "BTCUSDT",
    "bot_uuid": "d97dabb2-b1c3-4596-baa1-ae8c5f23ebb6"
  }'
```

Response (200 OK):
```json
{
  "status": "received",
  "action": "enter_long",
  "signal": "Buy",
  "trade_action": "BUY",
  "indicator_signals": {
    "indicator_a": "Buy",
    "indicator_b": "Buy"
  }
}
```

### Test 2: Send enter_short (Sell)
```bash
curl -X POST https://bottk.up.railway.app/webhook/3commas \
  -H "Content-Type: application/json" \
  -d '{
    "action": "enter_short",
    "timestamp": "2026-04-22T20:00:00",
    "trigger_price": "45000",
    "tv_exchange": "BINANCE",
    "tv_instrument": "BTCUSDT",
    "bot_uuid": "d97dabb2-b1c3-4596-baa1-ae8c5f23ebb6"
  }'
```

Response (200 OK):
```json
{
  "status": "received",
  "action": "enter_short",
  "signal": "Sell",
  "trade_action": "SELL",
  "indicator_signals": {
    "indicator_a": "Sell",
    "indicator_b": "Sell"
  }
}
```

---

## In TradingView

Your indicator should look something like this (with your actual webhook URL):

```pinescript
if buy_signal
    request.post(url="https://bottk.up.railway.app/webhook/3commas",
        data='{"action": "enter_long", "timestamp": "' + str.tostring(time) + '", "trigger_price": "' + str.tostring(close) + '"}')

if sell_signal
    request.post(url="https://bottk.up.railway.app/webhook/3commas",
        data='{"action": "enter_short", "timestamp": "' + str.tostring(time) + '", "trigger_price": "' + str.tostring(close) + '"}')
```

Just change the URL from `https://api.3commas.io/signal_bots/webhooks` to `https://bottk.up.railway.app/webhook/3commas`

---

## Advantages of Using Your Bot

| Feature | 3Commas | Your Bot |
|---------|---------|----------|
| 10x Leverage | Yes | Yes |
| 90% Balance Usage | No | Yes (automatic) |
| Position Sizing | Manual | Automatic |
| Stop Loss | Manual setup | 24% or 2.4% (automatic) |
| No 3Commas Fees | No | Yes (saves money!) |
| Direct Bybit Control | No | Yes |
| Custom Logic | Limited | Full control |

---

## Webhook URL Summary

```
New Webhook URL: https://bottk.up.railway.app/webhook/3commas
Method: POST
Content-Type: application/json
Format: 3Commas standard format (no changes needed)
```

---

## Monitoring Your Bot

### Check Status
```bash
curl https://bottk.up.railway.app/status | jq '.indicator_signals'
```

### View Logs
```bash
railway logs --service trading-bot
```

### Test Webhook
```bash
curl -X POST https://bottk.up.railway.app/webhook/3commas \
  -H "Content-Type: application/json" \
  -d '{"action": "enter_long"}'
```

---

## Migration Steps

1. **Copy your current webhook URL** - Keep it for reference
2. **Note the payload format** - It stays the same
3. **Update the URL** in TradingView to `https://bottk.up.railway.app/webhook/3commas`
4. **Send a test signal** to verify
5. **Monitor your first few trades** to ensure everything works
6. **Keep 3Commas webhook as backup** (just in case)

---

## Important Notes

- Your indicator script **DOES NOT CHANGE**
- Only the webhook URL changes
- All payload data stays the same
- Your bot receives and converts automatically
- Trading starts immediately when signal is received

---

## Support

If you encounter issues:

1. Check the webhook URL is correct
2. Test with curl command above
3. Monitor logs: `railway logs --service trading-bot`
4. Verify Bybit API connection works
5. Check that bot is receiving signals

**Everything is set up and ready to go!** Just update the webhook URL. 🚀
