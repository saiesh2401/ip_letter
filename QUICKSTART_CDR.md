# 🔍 CDR Analyzer - Quick Start Guide

## Your CDR Analyzer is Ready!

The CDR analyzer is a **separate, standalone Streamlit application** located at:
- **Main App**: `cdr_app.py`
- **Test Script**: `test_cdr.py`
- **Launcher**: `run_cdr_analyzer.sh`

---

## 🚀 How to Run

### Option 1: Using the Launcher Script (Easiest)
```bash
cd /Users/saieshsingh/Desktop/projects/ifso
./run_cdr_analyzer.sh
```

### Option 2: Direct Streamlit Command
```bash
cd /Users/saieshsingh/Desktop/projects/ifso
streamlit run cdr_app.py
```

### Option 3: Test Without UI
```bash
cd /Users/saieshsingh/Desktop/projects/ifso
python3 test_cdr.py
```

---

## 📊 What You'll See

When you run the app, you'll get:

### **Welcome Screen** (Before Upload)
- Feature showcase with 8 key capabilities
- Upload button in sidebar
- Professional gradient design

### **After Uploading CDR File** (7 Analysis Tabs)

#### 1. 📊 **Dashboard**
- Total records, unique contacts, voice calls, SMS count
- Night activity percentage with alerts
- Daily activity timeline chart
- Hourly distribution bar chart
- Communication type pie chart
- Top 10 contacts visualization

#### 2. 🌙 **Temporal Analysis** (STATE-OF-THE-ART)
- **Night vs Day Summary Cards**
  - Night: 304 activities (9.5%)
  - Day: 2,120 activities (66.0%)
  - Evening: 786 activities (24.5%)
  
- **Suspicious Pattern Alerts**
  - Excessive night activity warnings
  - Late night (00:00-04:00) tracking
  
- **24-Hour Activity Heatmap**
  - Color-coded time periods
  - Red = Late Night/Night
  - Orange = Morning
  - Green = Afternoon
  - Blue = Evening
  
- **Detailed Breakdowns**
  - Night activity by time slots
  - Top night contacts
  - Top day contacts
  - Call duration statistics
  
- **Burst Activity Detection**
  - Statistical anomaly detection
  - Shows periods with unusual spikes

#### 3. 👥 **Contact Network**
- Contact frequency metrics
- Contact clustering (very frequent, frequent, moderate, occasional, one-time)
- Pie chart of contact distribution
- Top 15 contacts bar chart
- Interactive network graph visualization

#### 4. 🗺️ **Location Intelligence**
- Unique tower count
- Night vs day location metrics
- **Interactive Folium Map**
  - Filter by: All/Night/Day/Evening
  - Circle markers sized by frequency
  - Color-coded by time period
- Top 10 locations table with coordinates

#### 5. 📞 **Communication Patterns**
- Call duration statistics
- Daily activity metrics
- Day of week distribution chart
- Short/long call detection

#### 6. 🔍 **Search & Filter**
- Search by phone number
- Filter by call type
- Filter by time period
- Date range selection
- Export filtered results to CSV

#### 7. 📄 **Reports**
- Generate investigation reports
- Key findings summary
- Statistical analysis

---

## 📁 Sample Data Included

Your sample CDR file is already loaded:
- **File**: `CDR/7404154477_2.csv`
- **Records**: 3,210
- **Date Range**: May 1, 2024 - Nov 28, 2024
- **Unique Contacts**: 228
- **Night Activity**: 9.5%
- **Tower Locations**: 217

---

## 🎨 UI Features

### Premium Design Elements
- **Gradient color scheme** (#667eea to #764ba2)
- **Custom CSS styling** for professional look
- **Metric cards** with visual hierarchy
- **Alert boxes** for suspicious patterns
- **Interactive charts** with Plotly
- **Maps** with Folium
- **Responsive layout**

### Color Coding
- 🔴 **Red** - Night/Late night activities
- 🟠 **Orange** - Morning activities
- 🟢 **Green** - Afternoon activities
- 🔵 **Blue** - Evening activities
- ⚠️ **Yellow** - Alerts and warnings

---

## 💡 Usage Tips

### 1. **Upload Your CDR File**
- Click "Upload CDR File" in sidebar
- Select your Airtel CDR CSV file
- Click "Parse CDR File"
- Wait for parsing to complete

### 2. **Navigate Tabs**
- Start with Dashboard for overview
- Go to Temporal Analysis for night/day patterns
- Check Contact Network for relationships
- View Location Intelligence for tower mapping

### 3. **Export Data**
- Use Search & Filter tab
- Apply your filters
- Click "Export Filtered Results to CSV"

### 4. **Generate Reports**
- Go to Reports tab
- Select report type
- Click "Generate Report"

---

## 🔒 Security Note

This tool handles sensitive law enforcement data. Remember to:
- ✅ Keep CDR files secure
- ✅ Use in authorized environments only
- ✅ Follow data protection protocols
- ✅ Clear session data after use

---

## 📞 Quick Test

Run this to verify everything works:
```bash
python3 test_cdr.py
```

Expected output:
```
============================================================
CDR ANALYZER - TEST SCRIPT
============================================================

📁 Parsing CDR file...
✅ Successfully parsed 3210 records

📊 Basic Statistics:
  • Date range: 2024-05-01 09:20:44 to 2024-11-28 18:51:35
  • Unique contacts: 228
  • Total duration: 16.7 hours

🌙 Temporal Analysis:
  • Night activity: 304 (9.5%)
  • Day activity: 2120 (66.0%)
  • Evening activity: 786 (24.5%)
```

---

## 🎯 Key Features Recap

✅ **Advanced Temporal Analysis** - Night/day patterns, burst detection  
✅ **Contact Network Mapping** - Relationship graphs, clustering  
✅ **Location Intelligence** - Tower maps, movement tracking  
✅ **Communication Analytics** - Duration, frequency, patterns  
✅ **Search & Filter** - Multi-criteria filtering with export  
✅ **Report Generation** - Automated investigation summaries  
✅ **Premium UI/UX** - Professional design with visualizations  
✅ **Real-time Analysis** - Instant filtering and updates  

---

## 📚 Documentation

- **Full Guide**: [README_CDR.md](file:///Users/saieshsingh/Desktop/projects/ifso/README_CDR.md)
- **Walkthrough**: Check artifacts for detailed feature walkthrough
- **Code**: All modules are well-documented with inline comments

---

## 🚀 Ready to Use!

Your CDR analyzer is **production-ready** and tested with real data. Just run:

```bash
./run_cdr_analyzer.sh
```

Or:

```bash
streamlit run cdr_app.py
```

The app will open at **http://localhost:8501** 🎉
