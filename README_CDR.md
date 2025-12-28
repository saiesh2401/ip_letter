# CDR Analyzer - Law Enforcement Edition

## 🔍 Overview

State-of-the-art Call Detail Record (CDR) analysis tool specifically designed for law enforcement investigations. This application provides comprehensive analytics, advanced temporal pattern detection, location intelligence, and network analysis capabilities.

## ✨ Key Features

### 🌙 **Advanced Temporal Analysis**
- **Night vs Day Pattern Detection**: Comprehensive breakdown of activity across 24 hours
- **Burst Activity Detection**: Identifies periods of unusually high communication
- **Suspicious Pattern Alerts**: Automatic detection of excessive night activity
- **Time Period Classification**: Late night, morning, afternoon, evening, and night segments
- **Peak Hour Identification**: Identifies busiest hours for overall, night, and day activity

### 👥 **Contact Network Analysis**
- **Network Graph Visualization**: Interactive relationship mapping
- **Contact Clustering**: Categorizes contacts by interaction frequency
- **Top Contacts Identification**: Ranks most frequent communications
- **New Contact Timeline**: Tracks when new contacts first appear
- **Common Contact Detection**: Find shared contacts between multiple CDRs

### 🗺️ **Location Intelligence**
- **Tower Location Mapping**: Interactive maps showing cell tower locations
- **Movement Pattern Analysis**: Tracks movement between locations
- **Time-based Location Analysis**: Separate night/day/evening location patterns
- **Frequent Location Identification**: Identifies most visited areas
- **Geospatial Visualization**: Folium-based interactive maps

### 📊 **Communication Pattern Analysis**
- **Call Duration Statistics**: Total, average, median, max durations
- **Daily Activity Patterns**: Average, max, min daily activity
- **Day of Week Distribution**: Activity patterns across the week
- **Call Type Breakdown**: Voice, SMS, incoming, outgoing analysis
- **Short/Long Call Detection**: Identifies unusual call durations

### 🔍 **Advanced Search & Filter**
- Multi-criteria search (number, date range, call type, time period)
- Real-time filtering with instant results
- Export filtered results to CSV
- Custom date range selection

### 📄 **Report Generation**
- Automated investigation summaries
- Key findings extraction
- Visual evidence compilation
- Export capabilities

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory:**
```bash
cd /Users/saieshsingh/Desktop/projects/ifso
```

2. **Install dependencies:**
```bash
pip install -r requirements_cdr.txt
```

## 📖 Usage

### Running the Application

```bash
streamlit run cdr_app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Loading CDR Data

1. Click on the **"Upload CDR File"** button in the sidebar
2. Select your Airtel CDR CSV file
3. Click **"Parse CDR File"**
4. Wait for parsing to complete

### Navigating the Interface

The application has 7 main tabs:

#### 1. 📊 Dashboard
- Overview of key metrics
- Daily and hourly activity charts
- Call type distribution
- Top contacts visualization

#### 2. 🌙 Temporal Analysis
- **Night vs Day breakdown** with detailed statistics
- **24-hour activity heatmap** with color-coded time periods
- **Suspicious pattern detection** with alerts
- **Burst activity identification** showing unusual spikes
- **Top contacts by time period** (night/day)

#### 3. 👥 Contact Network
- Contact frequency distribution
- Network graph visualization
- Contact clustering (very frequent, frequent, moderate, occasional, one-time)
- Top 15 contacts bar chart

#### 4. 🗺️ Location Intelligence
- Interactive tower location maps
- Filter by time period (All/Night/Day/Evening)
- Top 10 locations table
- Movement pattern analysis

#### 5. 📞 Communication Patterns
- Call duration statistics
- Daily activity metrics
- Day of week distribution
- Behavioral insights

#### 6. 🔍 Search & Filter
- Search by phone number
- Filter by call type
- Filter by time period
- Date range selection
- Export filtered results

#### 7. 📄 Reports
- Generate investigation reports
- Summary statistics
- Key findings
- Export capabilities

## 🎯 Law Enforcement Use Cases

### 1. **Suspect Activity Monitoring**
- Track communication patterns over time
- Identify unusual behavior (excessive night activity, burst communications)
- Monitor contact networks and relationships

### 2. **Network Investigation**
- Map relationships between suspects
- Identify common contacts
- Detect new contacts and their introduction timeline

### 3. **Location Tracking**
- Track suspect movements via cell tower data
- Identify frequent locations (home, work, meeting places)
- Analyze night vs day location patterns

### 4. **Temporal Pattern Analysis**
- Detect suspicious timing (late-night communications)
- Identify peak activity periods
- Correlate events with specific timeframes

### 5. **Evidence Collection**
- Generate comprehensive reports
- Export filtered data for court proceedings
- Visual evidence (charts, maps, network graphs)

## 📊 Data Format

The application supports **Airtel CDR format** with the following key fields:

- **Target No**: Subject phone number
- **Call Type**: IN, OUT, SMT, SMO
- **B Party No**: Contact phone number
- **Date/Time**: Communication timestamp
- **Dur(s)**: Call duration in seconds
- **First/Last CGI Lat/Long**: Cell tower coordinates
- **IMEI/IMSI**: Device identifiers
- **Service Type**: Voice, SMS, Data

## 🔒 Security Considerations

> **⚠️ IMPORTANT**: This tool handles sensitive law enforcement data.

**Recommended Security Measures:**
- Implement access control and authentication
- Enable audit logging of all operations
- Use data encryption at rest and in transit
- Implement role-based permissions
- Secure file upload and storage
- Regular security audits
- Compliance with data protection regulations

## 🛠️ Technical Architecture

### Backend Modules

- **`cdr_parser.py`**: Robust CDR file parsing with error handling
- **`cdr_analyzer.py`**: Advanced analytics and pattern detection
- **`network_analyzer.py`**: Contact network analysis and graph generation
- **`location_analyzer.py`**: Location intelligence and movement tracking

### Frontend

- **`cdr_app.py`**: Streamlit-based web application with premium UI/UX

### Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **streamlit**: Web application framework
- **plotly**: Interactive visualizations
- **folium**: Map visualizations
- **networkx**: Network graph analysis

## 📈 Performance

- Handles CDR files with **thousands of records**
- Real-time filtering and search
- Optimized data processing
- Responsive visualizations

## 🐛 Troubleshooting

### Common Issues

**1. Datetime parsing errors**
- Ensure CDR file has proper date/time format (DD/MM/YYYY HH:MM:SS)
- Check for missing or malformed timestamps

**2. Location data not showing**
- Verify CDR contains valid latitude/longitude coordinates
- Check "First CGI Lat/Long" column format

**3. Slow performance**
- Large files (>10,000 records) may take longer to process
- Consider filtering data by date range

## 📝 Future Enhancements

- [ ] Multi-CDR comparison
- [ ] AI-powered anomaly detection
- [ ] Advanced geofencing alerts
- [ ] PDF report generation
- [ ] Database integration
- [ ] User authentication system
- [ ] Real-time CDR monitoring
- [ ] Cross-reference with other data sources

## 👨‍💻 Development

### Project Structure
```
ifso/
├── cdr_app.py              # Main Streamlit application
├── cdr_parser.py           # CDR parsing module
├── cdr_analyzer.py         # Analysis engine
├── network_analyzer.py     # Network analysis
├── location_analyzer.py    # Location intelligence
├── requirements_cdr.txt    # Python dependencies
└── CDR/                    # CDR data files
    └── 7404154477_2.csv   # Sample CDR file
```

## 📄 License

This tool is designed for law enforcement use only. Unauthorized use is prohibited.

## 🤝 Support

For issues, questions, or feature requests, please contact the development team.

---

**Built with ❤️ for Law Enforcement Professionals**

*State-of-the-Art CDR Analysis | Advanced Temporal Intelligence | Network Mapping | Location Tracking*
