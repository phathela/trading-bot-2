# Railway Deployment Instructions

Your GitHub repository is ready: **https://github.com/phathela/trading-bot**

## Step 1: Create Railway Project from GitHub (2 minutes)

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Search for and select **"trading-bot"**
5. Railway will auto-detect the Dockerfile and start deployment
6. Wait 2-3 minutes for build to complete

## Step 2: Configure Environment Variables (3 minutes)

Once deployment shows "Building" or "Deploying":

1. Click on the **"trading-bot"** service/deployment
2. Go to the **"Variables"** tab
3. Add these environment variables:

```
BYBIT_API_KEY=your_actual_bybit_api_key_here
BYBIT_API_SECRET=your_actual_bybit_api_secret_here
WEBHOOK_KEY=generate_a_secure_random_key_here
SYMBOL=BTCUSDT
TESTNET=True
PORT=5000
DEBUG=False
```

**For WEBHOOK_KEY, generate a secure key:**
- Windows PowerShell:
```powershell
[System.Convert]::ToHexString((1..32 | ForEach-Object { [byte](Get-Random -Maximum 256) }))
```

- Or use: `openssl rand -hex 32` (if you have it installed)

4. Click **"Deploy"** to redeploy with the new variables

## Step 3: Get Your Deployment URL (1 minute)

1. Go to the **"Deployments"** tab
2. Look for your active deployment
3. In the deployment details, you'll see a URL like:
   ```
   https://trading-bot-prod-xxxxxx.railway.app
   ```
4. Copy this URL - you'll need it for TradingView webhooks

## Step 4: Verify Deployment

Test your deployment:

```bash
# Health check
curl https://YOUR-DEPLOYMENT-URL/health

# Configuration
curl https://YOUR-DEPLOYMENT-URL/config

# Status (note: will show balance 0 until you test with real API keys)
curl https://YOUR-DEPLOYMENT-URL/status
```

## Step 5: Switch from TESTNET to LIVE (When Ready)

**After testing in testnet for at least 1 week:**

1. Go to Railway dashboard
2. Click on "trading-bot" deployment
3. Go to **"Variables"** tab
4. Change:
   - `TESTNET=False`
   - `BYBIT_API_KEY=your_live_api_key`
   - `BYBIT_API_SECRET=your_live_api_secret`
5. Click **"Deploy"** to activate

## Step 6: Set Up TradingView Webhooks

In your TradingView indicator script, use:

```
https://YOUR-DEPLOYMENT-URL/webhook
```

Example webhook payload:
```json
{
  "indicator": "indicator_a",
  "signal": "Buy"
}
```

With header:
```
X-Webhook-Key: your_webhook_key_from_step_2
```

## Monitoring Deployment

### View Logs
```bash
# Via Railway CLI
railway logs --service trading-bot

# Or in Railway dashboard:
# Deployments → Select deployment → Logs tab
```

### Check Status
```bash
curl https://YOUR-DEPLOYMENT-URL/status
```

## Troubleshooting

### Deployment fails to build
- Check Dockerfile exists
- View logs in Railway dashboard
- Verify all required files are in repository

### Bot not responding
- Check health endpoint: `/health`
- View deployment logs
- Verify environment variables are set
- Check Bybit API keys are correct

### Webhook not triggering trades
- Verify webhook URL is correct
- Check webhook key matches in Railway variables
- Test with curl first
- Check deployment logs for webhook requests

### No balance/position info
- Verify Bybit API keys are valid
- Check you're using correct testnet/live keys
- Ensure Bybit API key has trading permissions

## Quick Troubleshooting Checklist

- [ ] GitHub repo created: ✓ https://github.com/phathela/trading-bot
- [ ] GitHub authenticated: ✓ (you're logged in as phathela)
- [ ] Railway project deployed
- [ ] Environment variables set
- [ ] Deployment URL obtained
- [ ] Health check working
- [ ] Webhook URL in TradingView
- [ ] Test webhooks received

## Getting Help

1. Check Railway logs first
2. Test endpoints manually with curl
3. Verify environment variables in Railway dashboard
4. Check GitHub repo for latest code
5. Review SETUP.md and README.md in repo

## Important Notes

- Railway builds and deploys automatically when you push to GitHub
- The bot runs on a single dyno (suitable for webhook-based trading)
- Your API keys are stored securely in Railway's environment variables
- Logs are accessible via Railway dashboard or `railway logs` CLI

---

**Your GitHub repo:** https://github.com/phathela/trading-bot

**Next:** Complete steps 1-4 above, then let me know your deployment URL!
