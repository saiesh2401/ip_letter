# Multi-Format CDR Support

## 📱 Supported CDR Formats

The CDR Analyzer now supports **multiple CDR formats** with automatic format detection!

---

## ✅ Supported Formats

### 1. **Airtel CDR Format**
- **Operator**: Bharti Airtel Limited
- **GPS Coordinates**: ✅ Available (`First CGI Lat/Long`, `Last CGI Lat/Long`)
- **Cell ID Format**: `404-96-290-128686112` (MCC-MNC-LAC-CellID)
- **Date Format**: `DD/MM/YYYY`
- **Time Format**: `HH:MM:SS`
- **Key Columns**:
  - `Target No`
  - `Call Type` (IN, OUT, SMT, SMO)
  - `Date`, `Time`
  - `Dur(s)`
  - `First CGI Lat/Long`, `Last CGI Lat/Long`
  - `First CGI`, `Last CGI`
  - `B Party No`
  - `IMEI`, `IMSI`

### 2. **Jio CDR Format** ⭐ NEW
- **Operator**: Reliance Jio
- **GPS Coordinates**: ❌ Not available (use Cell Tower Database instead!)
- **Cell ID Format**: `4058722113210` (different format)
- **Date Format**: `DD/MM/YYYY`
- **Time Format**: `HH:MM:SS`
- **Key Columns**:
  - `Calling Party Telephone Number`
  - `Called Party Telephone Number`
  - `Call Type` (a_in, a_out, A2P_SMSIN, P2P_SMSIN, etc.)
  - `Call Date`, `Call Time`
  - `Call Duration`
  - `First Cell ID`, `Last Cell ID`
  - `IMEI`, `IMSI`
  - `Roaming Circle Name`

---

## 🔍 Automatic Format Detection

The parser **automatically detects** which format your CDR is in!

**Detection Logic:**
1. Scans first 20 lines of the file
2. Looks for format-specific indicators:
   - **Airtel**: "BHARTI AIRTEL", "Target No", "Call Type"
   - **Jio**: "Calling Party Telephone Number", "Ticket Number"
3. Parses accordingly

**You don't need to do anything** - just upload your CDR file!

---

## 📊 Feature Comparison

| Feature | Airtel | Jio |
|---------|--------|-----|
| GPS Coordinates | ✅ Yes | ❌ No |
| Cell Tower IDs | ✅ Yes | ✅ Yes |
| Call Duration | ✅ Yes | ✅ Yes |
| Contact Numbers | ✅ Yes | ✅ Yes |
| IMEI/IMSI | ✅ Yes | ✅ Yes |
| Roaming Info | ✅ Yes | ✅ Yes |
| Temporal Analysis | ✅ Yes | ✅ Yes |
| Network Analysis | ✅ Yes | ✅ Yes |
| **Location Intelligence** | ✅ Full | ⚠️ Cell Tower Lookup Only |

---

## 🗺️ Location Intelligence for Jio CDRs

Since Jio CDRs **don't include GPS coordinates**, you need to use the **Cell Tower Database Lookup** feature!

### How to Get Locations for Jio CDRs:

1. Upload your Jio CDR file
2. Go to **"Location Intelligence"** tab
3. Click **"🔍 Lookup Cell Towers"** button
4. Wait for the system to fetch tower locations from Mozilla MLS (free!)
5. View the map with tower locations

**Note**: The Cell Tower Database will convert Cell IDs to approximate GPS coordinates.

---

## 🎯 Usage Examples

### Airtel CDR:
```
Upload: airtel.csv
✅ Auto-detected: AIRTEL format
✅ GPS coordinates: Available
✅ Location map: Shows exact GPS locations
✅ Cell tower lookup: Optional (for verification)
```

### Jio CDR:
```
Upload: jio.csv
✅ Auto-detected: JIO format
⚠️ GPS coordinates: Not available
✅ Cell tower lookup: REQUIRED for location intelligence
✅ Location map: Shows after cell tower lookup
```

---

## 📝 Call Type Classifications

### Airtel Call Types:
- `IN` → Incoming Call
- `OUT` → Outgoing Call
- `SMT` → SMS Received
- `SMO` → SMS Sent

### Jio Call Types:
- `a_in` → Incoming Call
- `a_out` → Outgoing Call
- `A2P_SMSIN` → SMS Received (Application to Person)
- `P2P_SMSIN` → SMS Received (Person to Person)
- `P2AOUT` → SMS Sent

---

## 🔧 Technical Details

### Parser Architecture:

```python
class CDRParser:
    def parse():
        1. Detect format (Airtel or Jio)
        2. Extract metadata
        3. Parse based on format:
           - _parse_airtel() for Airtel
           - _parse_jio() for Jio
        4. Standardize columns
        5. Return unified DataFrame
```

### Standardized Output:

Both formats are converted to a **unified schema**:
- `DateTime` - Parsed datetime
- `Hour`, `DayOfWeek`, `Date_Only` - Temporal features
- `TimePeriod` - Classified time period
- `Dur(s)` - Call duration in seconds
- `First_Lat`, `First_Long` - GPS coordinates (or None for Jio)
- `Last_Lat`, `Last_Long` - GPS coordinates (or None for Jio)
- `First CGI`, `Last CGI` - Cell IDs
- `B_Party_Clean` - Cleaned contact number
- `Call_Category` - Standardized call type
- `Is_Night`, `Is_Day`, `Is_Evening` - Time flags

---

## ⚡ Performance

- **Airtel CDR** (3,210 records): ~2 seconds
- **Jio CDR** (470 records): ~1 second
- **Cell Tower Lookup** (200 unique towers): ~2-3 minutes

---

## 🚨 Important Notes

### For Jio CDRs:

1. **No GPS Coordinates**: Jio CDRs don't include GPS data
2. **Cell Tower Lookup Required**: Use the Cell Tower Database feature
3. **Cell ID Format Different**: Jio uses different Cell ID format
4. **Movement Timeline**: Will only work after cell tower lookup

### For Airtel CDRs:

1. **GPS Included**: Direct GPS coordinates available
2. **Cell Tower Lookup Optional**: Can verify GPS accuracy
3. **Full Location Intelligence**: All features work immediately

---

## 📖 Example Workflow

### Analyzing Jio CDR:

1. **Upload** `jio.csv`
   - System detects: "JIO format"
   
2. **Dashboard Tab**
   - View call statistics
   - See temporal patterns
   
3. **Temporal Analysis Tab**
   - Night/day activity
   - Burst detection
   
4. **Contact Network Tab**
   - Top contacts
   - Network graph
   
5. **Location Intelligence Tab**
   - ⚠️ Map will be empty initially
   - Click "🔍 Lookup Cell Towers"
   - Wait for lookup to complete
   - ✅ Map now shows tower locations
   - View animated timeline
   
6. **Communication Patterns Tab**
   - Call duration analysis
   - Daily patterns

---

## 🎉 Summary

**Multi-format support is now live!**

✅ **Airtel CDRs**: Full support with GPS  
✅ **Jio CDRs**: Full support with Cell Tower lookup  
✅ **Auto-detection**: No manual configuration needed  
✅ **Unified analysis**: Same features for both formats  

**Just upload your CDR and start analyzing!** 🚀

---

## 🔗 Related Documentation

- [Cell Tower Database Setup](file:///Users/saieshsingh/Desktop/projects/ifso/CELL_TOWER_SETUP.md)
- [CDR Analyzer README](file:///Users/saieshsingh/Desktop/projects/ifso/README_CDR.md)
- [Quick Start Guide](file:///Users/saieshsingh/Desktop/projects/ifso/QUICKSTART_CDR.md)
