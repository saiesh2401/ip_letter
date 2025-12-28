# Cell Tower Database - Setup Guide

## 🗼 Open-Source Cell Tower Databases

The CDR Analyzer now supports looking up cell tower locations from Cell IDs using **free, open-source databases**.

---

## 📡 Available Databases

### 1. **Mozilla Location Service (MLS)** ⭐ RECOMMENDED
- **Website**: https://location.services.mozilla.com/
- **API Key**: ❌ Not required
- **Cost**: ✅ Free
- **Rate Limit**: Unlimited (fair use policy)
- **Coverage**: Global
- **Status**: **Active by default**

**Why use MLS?**
- No registration needed
- No API key required
- Good global coverage
- Maintained by Mozilla Foundation
- Works out of the box!

---

### 2. **OpenCelliD**
- **Website**: https://opencellid.org/
- **API Key**: ✅ Required (free)
- **Cost**: ✅ Free tier available
- **Rate Limit**: 1,000 requests/day (free tier)
- **Coverage**: Global (40M+ cell towers)
- **Status**: Optional (requires API key)

**How to get API key:**
1. Visit https://opencellid.org/
2. Register for free account
3. Get your API key from dashboard
4. Set environment variable: `export OPENCELLID_API_KEY=your_key_here`

---

### 3. **Unwired Labs**
- **Website**: https://unwiredlabs.com/
- **API Key**: ✅ Required (free)
- **Cost**: ✅ Free tier available
- **Rate Limit**: 100 requests/day (free tier)
- **Coverage**: Global
- **Status**: Optional (requires API key)

**How to get API key:**
1. Visit https://unwiredlabs.com/
2. Sign up for free account
3. Get your API token
4. Set environment variable: `export UNWIRED_API_KEY=your_token_here`

---

## 🚀 Quick Start (No Setup Required!)

The CDR Analyzer works **immediately** with Mozilla Location Service - no configuration needed!

Just:
1. Upload your CDR file
2. Go to **Location Intelligence** tab
3. Click **"Lookup Cell Towers"** button
4. Wait for results

---

## 🔧 Advanced Setup (Optional)

For better coverage and higher rate limits, add API keys:

### On Mac/Linux:
```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENCELLID_API_KEY="your_opencellid_key"
export UNWIRED_API_KEY="your_unwired_token"

# Reload shell
source ~/.zshrc
```

### On Windows:
```cmd
# Set environment variables
setx OPENCELLID_API_KEY "your_opencellid_key"
setx UNWIRED_API_KEY "your_unwired_token"
```

---

## 📊 How It Works

### Cell ID Format
CDR files contain Cell IDs in format: `MCC-MNC-LAC-CellID`

Example: `404-96-290-128686112`
- **MCC**: 404 (India)
- **MNC**: 96 (Airtel)
- **LAC**: 290 (Location Area Code)
- **CellID**: 128686112 (Specific tower)

### Lookup Process
1. Parse Cell ID from CDR
2. Query Mozilla MLS API (free, no key)
3. If not found, try OpenCelliD (if key available)
4. If not found, try Unwired Labs (if key available)
5. Cache results to avoid duplicate lookups
6. Return latitude/longitude of cell tower

---

## 🎯 Use Cases

### 1. **Verify GPS Accuracy**
- Compare GPS coordinates with cell tower location
- Identify GPS spoofing or errors
- Calculate distance between GPS and tower

### 2. **Fill Missing GPS Data**
- Some CDR records may lack GPS coordinates
- Cell tower location provides approximate position
- Better than no location data

### 3. **Historical Analysis**
- Cell tower locations are more stable than GPS
- Useful for old CDR data
- Less affected by GPS signal issues

### 4. **Coverage Analysis**
- Identify which towers suspect used
- Map tower coverage areas
- Analyze roaming patterns

---

## 📈 Performance

### Sample Results (3,210 records):
- **Unique Cell IDs**: ~217
- **Successful Lookups**: ~180-200 (depends on database coverage)
- **Lookup Time**: ~2-3 minutes (with rate limiting)
- **Cache**: Subsequent lookups instant
- **Average GPS vs Tower Distance**: 0.5-2 km

---

## 💡 Tips

1. **Use Mozilla MLS First**: It's free and works without setup
2. **Add API Keys Later**: Only if you need better coverage
3. **Check Cache**: Results are cached in `cell_tower_cache.json`
4. **Rate Limiting**: APIs have delays to respect rate limits
5. **Comparison**: Always compare with GPS coordinates

---

## 🔍 Example Output

```
Cell Tower Database Lookup
==========================

Available Databases:
✅ Mozilla Location Service - Active
⚠️ OpenCelliD - API key not configured
⚠️ Unwired Labs - API key not configured

[Click: Lookup Cell Towers]

✅ Found 187/217 cell tower locations!

📊 Cell Tower vs GPS Comparison:
┌──────────────────────┬─────────────────┬───────────┬────────────┬──────────────┬─────────────┐
│ DateTime             │ Cell ID         │ GPS Lat   │ GPS Long   │ Tower Lat    │ Tower Long  │
├──────────────────────┼─────────────────┼───────────┼────────────┼──────────────┼─────────────┤
│ 2024-05-01 09:20:44  │ 404-96-290-...  │ 28.79852  │ 76.17299   │ 28.79800     │ 76.17250    │
└──────────────────────┴─────────────────┴───────────┴────────────┴──────────────┴─────────────┘

📏 Average distance between GPS and Cell Tower: 0.85 km
```

---

## 🛡️ Privacy & Security

- **No data sent to third parties** (except cell tower APIs)
- **Caching minimizes API calls**
- **Open-source databases** (community-maintained)
- **No personal data shared** (only cell tower IDs)
- **Local cache** stored in project directory

---

## 📚 API Documentation

- **Mozilla MLS**: https://mozilla.github.io/ichnaea/api/index.html
- **OpenCelliD**: https://opencellid.org/api
- **Unwired Labs**: https://unwiredlabs.com/docs

---

## ✅ Summary

**Out of the box**: Works with Mozilla MLS (free, no setup)  
**Optional**: Add OpenCelliD or Unwired Labs for better coverage  
**Use case**: Verify GPS, fill missing data, analyze tower usage  
**Performance**: ~2-3 minutes for 200 unique towers  

**Ready to use immediately!** 🚀
