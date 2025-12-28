# Cell Tower Location Lookup for Jio CDR

## Overview

The CDR Analyzer now supports **automatic cell tower location lookup** for both **Airtel** and **Jio** CDR formats. This feature converts Cell IDs into GPS coordinates (latitude/longitude) using free, open-source databases.

## Supported Formats

### Airtel Format
- **Column**: `First CGI`
- **Format**: Hyphenated (MCC-MNC-LAC-CellID)
- **Example**: `404-96-290-128686112`
  - MCC: 404 (India)
  - MNC: 96 (Airtel)
  - LAC: 290
  - Cell ID: 128686112

### Jio Format  
- **Column**: `First Cell ID`
- **Format**: Concatenated (MCCMNC + LAC + CellID)
- **Example**: `4058722113210`
  - MCC: 405 (India - Jio)
  - MNC: 872 (Jio network code)
  - LAC + Cell ID: 2113210 (parsed automatically)

## How It Works

### Cell Tower Databases Used

The system tries multiple free databases in order:

1. **Mozilla Location Service (MLS)** ✅ Recommended
   - **Free**: No API key required
   - **Rate Limit**: Unlimited (fair use)
   - **Coverage**: Global
   - **URL**: https://location.services.mozilla.com/

2. **OpenCelliD** (Optional)
   - **Free**: Requires API key (free registration)
   - **Rate Limit**: 1,000 requests/day
   - **Coverage**: Global
   - **URL**: https://opencellid.org/

3. **Unwired Labs** (Optional)
   - **Free**: Requires API key
   - **Rate Limit**: 100 requests/day
   - **Coverage**: Global
   - **URL**: https://unwiredlabs.com/

### Caching System

- All lookups are **cached locally** in `cell_tower_cache.json`
- Subsequent lookups for the same cell ID are instant
- Cache persists across sessions

## Using the Feature

### In the Streamlit App

1. **Upload your CDR file** (Jio or Airtel format)
2. **Navigate to "Location Intelligence" tab**
3. **Click "🔍 Lookup Cell Towers" button**
4. **Wait for the lookup to complete**
   - Progress is shown in the UI
   - Successful lookups are displayed

### What You Get

After lookup, the dataframe is enriched with:
- `Cell_Tower_Lat` - Latitude of the cell tower
- `Cell_Tower_Long` - Longitude of the cell tower
- `Cell_Tower_Source` - Which database provided the data

### Viewing Results

- **Map View**: Cell tower locations appear on the map
- **Comparison Table**: Shows GPS vs Cell Tower coordinates
- **Distance Calculation**: Average distance between GPS and cell tower

## Technical Details

### Jio Cell ID Parsing

The parser automatically detects Jio's format:

```python
# Example: 4058722113210
MCC = 405          # First 3 digits (India - Jio)
MNC = 872          # Next 3 digits (Jio network)
Remaining = 2113210  # LAC + Cell ID (split automatically)
```

### API Request Example

For Mozilla MLS:
```json
{
  "cellTowers": [{
    "radioType": "gsm",
    "mobileCountryCode": 405,
    "mobileNetworkCode": 872,
    "locationAreaCode": 211,
    "cellId": 3210
  }]
}
```

Response:
```json
{
  "location": {
    "lat": 28.7041,
    "lng": 77.1025
  },
  "accuracy": 500
}
```

## Limitations

1. **Accuracy**: Cell tower location ≠ exact device location
   - Cell coverage can be 1-5 km radius
   - Useful for general area, not precise location

2. **Coverage**: Not all cell towers are in databases
   - Rural areas may have less coverage
   - Newer towers may not be indexed yet

3. **Rate Limits**: Free APIs have limits
   - Mozilla MLS: Unlimited (fair use)
   - OpenCelliD: 1,000/day (with API key)
   - Unwired Labs: 100/day (with API key)

## Troubleshooting

### No Results Found

**Possible reasons**:
1. Cell ID not in database
2. Cell ID format not recognized
3. Network connectivity issues
4. API rate limit reached

**Solutions**:
- Check if cell IDs are in correct format
- Try again later (rate limits reset daily)
- Register for OpenCelliD API key for more coverage

### Adding API Keys (Optional)

To use OpenCelliD or Unwired Labs:

```bash
# Set environment variables
export OPENCELLID_API_KEY="your_key_here"
export UNWIRED_API_KEY="your_key_here"

# Then restart the Streamlit app
streamlit run cdr_app.py
```

## Example Use Cases

### Investigation Scenario

1. **Upload Jio CDR** with cell IDs like `4058722113210`
2. **Lookup cell towers** to get GPS coordinates
3. **Filter by time**: "Calls Only" + "Night"
4. **View map**: See where suspect made calls at night
5. **Analyze patterns**: Identify frequent locations

### Comparison Analysis

- Compare GPS coordinates (if available) with cell tower locations
- Verify accuracy of location data
- Identify discrepancies

## Files Modified

- [`cell_tower_db.py`](file:///Users/saieshsingh/Desktop/projects/ifso/cell_tower_db.py) - Enhanced parser for Jio format
- [`cdr_app.py`](file:///Users/saieshsingh/Desktop/projects/ifso/cdr_app.py) - UI integration (already implemented)

## Next Steps

The cell tower lookup feature is **ready to use**! Simply:
1. Upload a Jio or Airtel CDR file
2. Go to Location Intelligence tab
3. Click "Lookup Cell Towers"
4. View the enriched location data on the map

The system will automatically detect the format and parse accordingly.
