# OrgLedger - Vercel Deployment Guide

## Overview
Your Flask + MongoDB Atlas app is now ready for Vercel deployment. All critical fixes have been applied.

---

## ✅ Fixes Applied

### 1. **Requirements File Created** ✓
- **Location**: `requirements.txt` (root directory)
- **Purpose**: Vercel needs this at root level, not just in `back-end/`
- **Contents**:
  ```
  Flask==3.0.0
  Flask-Cors==4.0.0
  pymongo==4.6.1
  dnspython==2.4.2
  Werkzeug==3.0.1
  ```
- **Why dnspython?** Required for `mongodb+srv://` connection strings used by MongoDB Atlas

### 2. **Flask App Hardened** ✓
- **Location**: `back-end/app.py`
- **Changes**:
  - Added environment detection (Vercel vs Local)
  - Wrapped blueprint imports in try-except (won't crash if imports fail)
  - Added `/health` endpoint for status checking
  - Removed dangerous patterns (kept `app.run()` only in local mode)
  - Added debug logging for troubleshooting

### 3. **MongoDB Connection Wrapped** ✓
- **Location**: `back-end/db.py`
- **Changes**:
  - Connection errors no longer crash the app
  - Collections set to `None` if MongoDB unavailable
  - Added specific error handling for timeouts
  - Added `retryWrites=True` and `w='majority'` for Atlas reliability

### 4. **Authentication Endpoints Protected** ✓
- **Location**: `back-end/routes/auth_routes.py`
- **Changes**:
  - All endpoints check if `users_collection is None`
  - Return **503 Service Unavailable** if database unreachable
  - Prevents 500 crashes; user sees clear error instead

### 5. **vercel.json Verified** ✓
- **Entry Point**: `"src": "back-end/app.py"` ← Correct
- **Routes**: API routes properly separated from static files
- **No changes needed** - already configured correctly

---

## 🚀 Deployment Steps

### Step 1: Commit Changes Locally
```bash
cd c:\Users\rimss\Desktop\OrgLedger - ITD110_CaseStudy_1
git add -A
git commit -m "Fix Vercel deployment: add requirements.txt at root, harden Flask app, wrap MongoDB connection"
git push
```

### Step 2: Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign in (or create account)
3. Click **"Add New..."** → **"Project"**
4. Select GitHub repository: **OrgLedger-ITD110_CaseStudy_1**
5. Click **Import**

### Step 3: Environment Variables
**CRITICAL**: Add MongoDB Atlas connection string:

1. In Vercel dashboard, click on your project
2. Go to **Settings** → **Environment Variables**
3. Add new variable:
   - **Name**: `MONGO_URI`
   - **Value**: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`
   
   > Get this from MongoDB Atlas:
   > - Atlas Dashboard → **Clusters** → **Connect**
   > - Choose **Python** driver
   > - Copy connection string and fill in username/password

4. Click **Save**

### Step 4: Deploy
1. Click **Deploy** button
2. Wait for build to complete (2-3 minutes)
3. You'll get a URL like: `https://yourproject.vercel.app`

---

## 🧪 Testing After Deployment

### Test 1: Health Check
```bash
curl https://yourproject.vercel.app/health
```
**Expected response**:
```json
{"status": "ok", "database": "connected"}
```

If it returns **database error**, your MONGO_URI is wrong → go back to Step 3.

### Test 2: Registration
```bash
curl -X POST https://yourproject.vercel.app/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"pass123"}'
```

**Expected response** (201):
```json
{"message": "User registered successfully", "user_id": "..."}
```

### Test 3: Login
```bash
curl -X POST https://yourproject.vercel.app/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'
```

**Expected response** (200):
```json
{"message": "Login successful", "user_id": "..."}
```

---

## 🔍 Troubleshooting

### Issue: 503 Service Unavailable
**Root Cause**: Database not connected

**Fix**:
1. Check MONGO_URI environment variable in Vercel dashboard
2. Verify MongoDB Atlas connection string format
3. Ensure IP whitelist includes Vercel's IPs (set to 0.0.0.0/0 for testing)

### Issue: FUNCTION_INVOCATION_FAILED
**Root Cause**: Usually missing `dnspython` or `pymongo`

**Fix**:
1. Verify `requirements.txt` exists at project root
2. Check all dependencies are listed (including `dnspython`)
3. Re-deploy

### Issue: 502 Bad Gateway
**Root Cause**: Blueprint import failed or syntax error

**Fix**:
1. Check Vercel Function logs: **Deployments** → **Logs**
2. Look for `[ERROR]` messages
3. Check terminal output from `python back-end/app.py` locally to replicate error

### Issue: "Cannot GET /register"
**Root Cause**: Route not properly registered

**Fix**:
1. Test `/health` endpoint first (verifies Flask is running)
2. Check Vercel logs for blueprint registration errors
3. Ensure all route files in `back-end/routes/` have correct imports

---

## 📊 Monitoring

### View Logs
1. In Vercel dashboard, select your project
2. Click **Deployments**
3. Click latest deployment
4. Click **Logs** tab
5. Look for `[DEBUG]` and `[ERROR]` messages

### Typical Startup Logs
```
[DEBUG] Flask app initialized
[DEBUG] Environment: Vercel
[DEBUG] Importing route blueprints...
[DEBUG] All blueprints registered successfully
[DEBUG] MongoDB connection string: mongodb+srv://...
[DEBUG] ✓ MongoDB connection successful
[DEBUG] ✓ Connected to database: expense_tracker
[DEBUG] Creating indexes...
[DEBUG] ✓ Indexes created successfully
```

If you don't see these, something failed during startup.

---

## 🔐 Production Security Checklist

- [ ] MONGO_URI added to Vercel environment variables
- [ ] MongoDB Atlas IP whitelist updated (allow Vercel IPs)
- [ ] API routes in `vercel.json` properly configured
- [ ] CORS enabled in `back-end/app.py` (already done)
- [ ] Frontend API URLs use relative paths (already done)
- [ ] No `app.run(debug=True)` executed on Vercel (only locally)
- [ ] All dependencies in `requirements.txt`
- [ ] No secrets in `.env` files (use Vercel dashboard)

---

## 📝 Summary

Your app is now **Vercel-ready**:

✅ Hardened Flask app with error handling
✅ MongoDB connection won't crash app
✅ Health check endpoint for monitoring
✅ Proper requirements.txt with all dependencies
✅ Database connection checks in all routes
✅ Comprehensive logging for debugging

**Next Action**: Commit, push, and deploy to Vercel following **Deployment Steps** above.

