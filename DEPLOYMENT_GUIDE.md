# 🚀 Quick Deployment Guide - Making Your API Accessible Remotely

## Option 1: Using ngrok (Fastest - For Testing)

### What is ngrok?
Creates a secure tunnel to your localhost, giving you a public URL that Gift can use to test immediately.

### Steps:

1. **Download ngrok**
   - Visit: https://ngrok.com/download
   - Sign up for free account
   - Download and extract

2. **Start your FastAPI server** (if not already running)
   ```bash
   cd d:\HoMS\backend
   python -m uvicorn main:app --port 8000
   ```

3. **In a new terminal, run ngrok**
   ```bash
   ngrok http 8000
   ```

4. **Copy the public URL**
   You'll see something like:
   ```
   Forwarding  https://abc123def456.ngrok.io -> http://localhost:8000
   ```

5. **Share with Gift**
   Tell Gift to use: `https://abc123def456.ngrok.io/summary`

### ⚠️ Limitations:
- URL changes every time you restart ngrok (free tier)
- Session expires after 2 hours (free tier)
- Good for testing only

---

## Option 2: Deploy to Render (Free - Production Ready)

### What is Render?
Free cloud hosting for your FastAPI app with permanent URL.

### Steps:

1. **Create account**
   - Visit: https://render.com
   - Sign up with GitHub

2. **Push code to GitHub** (if not already)
   ```bash
   cd d:\HoMS\backend
   git init
   git add .
   git commit -m "Initial backend setup"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/lemi-homs-backend.git
   git push -u origin main
   ```

3. **Create Web Service on Render**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: lemi-homs-backend
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   - In Render dashboard, go to "Environment"
   - Add your DATABASE_URL from `.env` file

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - You'll get a permanent URL: `https://lemi-homs-backend.onrender.com`

6. **Share with Gift**
   Tell Gift to use: `https://lemi-homs-backend.onrender.com/summary`

### ✅ Benefits:
- Free forever
- Permanent URL
- Auto-deploys on git push
- HTTPS included
- Production-ready

---

## Option 3: Local Network (If on Same WiFi)

### Steps:

1. **Find your IP address**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address": e.g., `192.168.1.100`

2. **Allow through Windows Firewall**
   ```bash
   netsh advfirewall firewall add rule name="FastAPI" dir=in action=allow protocol=TCP localport=8000
   ```

3. **Start server on all interfaces**
   ```bash
   cd d:\HoMS\backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Share with Gift**
   Tell Gift to use: `http://192.168.1.100:8000/summary`

### ⚠️ Limitations:
- Only works on same WiFi network
- Your computer must stay on
- IP might change if router restarts

---

## 🎯 Recommended Approach for Gift

**For immediate testing:**
1. Use **ngrok** - Get Gift testing in 5 minutes
2. Send him the integration guide
3. He can test while you deploy

**For permanent solution:**
1. Deploy to **Render** - Free and reliable
2. Update integration guide with permanent URL
3. Gift switches to production URL

---

## 📝 Files to Send Gift

1. **INTEGRATION_GUIDE_FOR_GIFT.md** ✅ (Already created)
2. **Your ngrok URL** or **Render URL** (after deployment)
3. **Test credentials** (if you add authentication later)

---

## 🧪 Test Deployment

After deploying, test with:

```bash
curl -X POST "https://YOUR_URL/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-31",
    "rooms_total": 20,
    "rooms_occupied": 8,
    "rooms_available": 12,
    "cash_collected": 350000,
    "momo_collected": 120000,
    "total_collected": 470000,
    "expected_balance": 470000,
    "expenses_logged": 20000
  }'
```

Or visit: `https://YOUR_URL/docs` to see if API docs load.

---

## 🆘 Need Help?

**ngrok not working?**
- Make sure local server is running first
- Check if port 8000 is correct

**Render deployment failing?**
- Check build logs in Render dashboard
- Ensure requirements.txt is complete
- Verify DATABASE_URL is added to environment variables

**Connection issues?**
- Test with browser: Visit `https://YOUR_URL/health`
- Should return: `{"status":"healthy","service":"backend-api"}`
