"""
CDR Analyzer - Law Enforcement Edition
State-of-the-art Call Detail Record Analysis Tool
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
import networkx as nx
from datetime import datetime, timedelta
import json

# Import custom modules
from cdr_parser import CDRParser
from cdr_analyzer import CDRAnalyzer
from network_analyzer import NetworkAnalyzer
from location_analyzer import LocationAnalyzer

# Page configuration
st.set_page_config(
    page_title="CDR Analyzer - Law Enforcement",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for FUTURISTIC 2071 STYLE
st.markdown("""
<style>
    /* Futuristic Background with Animated Gradient */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0a0e27 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Holographic Grid Overlay */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
    }
    
    /* Main Header with Neon Glow */
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f5ff 0%, #667eea 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(0, 245, 255, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
        letter-spacing: 2px;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px rgba(0, 245, 255, 0.5)); }
        to { filter: drop-shadow(0 0 20px rgba(0, 245, 255, 0.8)); }
    }
    
    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(0, 245, 255, 0.2);
        box-shadow: 
            0 8px 32px 0 rgba(0, 245, 255, 0.1),
            inset 0 0 20px rgba(0, 245, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 245, 255, 0.5);
        box-shadow: 
            0 12px 40px 0 rgba(0, 245, 255, 0.3),
            inset 0 0 30px rgba(0, 245, 255, 0.1);
    }
    
    /* Alert Boxes with Holographic Effect */
    .alert-box {
        background: rgba(255, 75, 75, 0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #ff4b4b;
        box-shadow: 
            0 0 20px rgba(255, 75, 75, 0.3),
            inset 0 0 20px rgba(255, 75, 75, 0.05);
        margin: 1rem 0;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 75, 75, 0.3); }
        50% { box-shadow: 0 0 30px rgba(255, 75, 75, 0.5); }
    }
    
    /* Success Boxes */
    .success-box {
        background: rgba(0, 255, 170, 0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #00ffaa;
        box-shadow: 0 0 20px rgba(0, 255, 170, 0.3);
        margin: 1rem 0;
    }
    
    /* Futuristic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 15px;
        border: 1px solid rgba(0, 245, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(0, 245, 255, 0.2);
        color: #00f5ff;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 245, 255, 0.1);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.2), rgba(102, 126, 234, 0.2));
        border-color: #00f5ff;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
    
    /* Metrics with Neon Effect */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        color: #00f5ff;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    /* Buttons with Holographic Style */
    .stButton button {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.2), rgba(102, 126, 234, 0.2));
        border: 2px solid #00f5ff;
        border-radius: 10px;
        color: #00f5ff;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.3), rgba(102, 126, 234, 0.3));
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.6);
        transform: translateY(-2px);
    }
    
    /* Sidebar with Futuristic Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.95), rgba(15, 52, 96, 0.95));
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 245, 255, 0.2);
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.1);
    }
    
    /* Dataframes with Glow */
    .dataframe {
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.2);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00f5ff, #667eea);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #667eea, #f093fb);
    }
    
    /* Dividers with Neon Glow */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00f5ff, transparent);
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        margin: 2rem 0;
    }
    
    /* Text with Cyber Glow */
    h1, h2, h3 {
        color: #00f5ff;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
    }
    
    /* Loading Animation */
    @keyframes scan {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100%); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cdr_data' not in st.session_state:
    st.session_state.cdr_data = None
if 'parsed_df' not in st.session_state:
    st.session_state.parsed_df = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 CDR Analyzer - Law Enforcement Edition</h1>', unsafe_allow_html=True)
    st.markdown("**State-of-the-Art Call Detail Record Analysis & Investigation Tool**")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📁 Upload CDR File")
        uploaded_file = st.file_uploader(
            "Upload Airtel CDR CSV",
            type=['csv'],
            help="Upload Call Detail Record file in Airtel format"
        )
        
        if uploaded_file:
            if st.button("🔄 Parse CDR File", type="primary", use_container_width=True):
                with st.spinner("Parsing CDR file..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Parse the file
                        parser = CDRParser(temp_path)
                        df = parser.parse()
                        
                        st.session_state.parsed_df = df
                        st.session_state.cdr_data = parser
                        st.session_state.analyzer = CDRAnalyzer(df)
                        
                        st.success(f"✅ Successfully parsed {len(df)} records!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error parsing file: {str(e)}")
        
        st.markdown("---")
        
        # Quick stats in sidebar
        if st.session_state.parsed_df is not None:
            df = st.session_state.parsed_df
            st.markdown("### 📊 Quick Stats")
            st.metric("Total Records", f"{len(df):,}")
            st.metric("Unique Contacts", f"{df['B_Party_Clean'].nunique():,}")
            st.metric("Date Range", f"{(df['DateTime'].max() - df['DateTime'].min()).days} days")
            
            night_pct = (df['Is_Night'].sum() / len(df) * 100)
            st.metric("Night Activity", f"{night_pct:.1f}%")
    
    # Main content
    if st.session_state.parsed_df is None:
        # Welcome screen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Advanced Analytics</h3>
                <p>Comprehensive temporal, spatial, and network analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>🌙 Night/Day Analysis</h3>
                <p>State-of-the-art temporal pattern detection</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>🗺️ Location Intelligence</h3>
                <p>Tower mapping and movement tracking</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("👈 Upload a CDR file from the sidebar to begin analysis")
        
        # Feature showcase
        st.markdown("### 🎯 Key Features")
        
        features = {
            "Temporal Analysis": "Advanced night/day patterns, burst detection, suspicious activity alerts",
            "Contact Network": "Relationship mapping, network graphs, common contact detection",
            "Location Intelligence": "Tower mapping, movement patterns, geofencing",
            "Communication Patterns": "Call duration analysis, frequency patterns, behavioral insights",
            "Device Tracking": "IMEI/IMSI changes, multiple device detection",
            "Search & Filter": "Advanced multi-criteria search and filtering",
            "Report Generation": "Automated investigation reports with visualizations",
            "Timeline Analysis": "Chronological event tracking and correlation"
        }
        
        cols = st.columns(2)
        for idx, (feature, description) in enumerate(features.items()):
            with cols[idx % 2]:
                st.markdown(f"**{feature}**")
                st.caption(description)
        
    else:
        # Main analysis interface
        df = st.session_state.parsed_df
        analyzer = st.session_state.analyzer
        
        # Create tabs
        tabs = st.tabs([
            "📊 Dashboard",
            "🌙 Temporal Analysis",
            "👥 Contact Network",
            "🗺️ Location Intelligence",
            "📞 Communication Patterns",
            "🔍 Search & Filter",
            "📄 Reports"
        ])
        
        # TAB 1: Dashboard
        with tabs[0]:
            render_dashboard(df, analyzer)
        
        # TAB 2: Temporal Analysis
        with tabs[1]:
            render_temporal_analysis(df, analyzer)
        
        # TAB 3: Contact Network
        with tabs[2]:
            render_contact_network(df, analyzer)
        
        # TAB 4: Location Intelligence
        with tabs[3]:
            render_location_intelligence(df, analyzer)
        
        # TAB 5: Communication Patterns
        with tabs[4]:
            render_communication_patterns(df, analyzer)
        
        # TAB 6: Search & Filter
        with tabs[5]:
            render_search_filter(df)
        
        # TAB 7: Reports
        with tabs[6]:
            render_reports(df, analyzer)


def render_dashboard(df, analyzer):
    """Render main dashboard"""
    st.markdown("## 📊 Investigation Dashboard")
    
    # Key metrics - Row 1: Overview
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate call and SMS counts
    incoming_calls = len(df[df['Call_Category'] == 'Incoming Call'])
    outgoing_calls = len(df[df['Call_Category'] == 'Outgoing Call'])
    sms_received = len(df[df['Call_Category'] == 'SMS Received'])
    sms_sent = len(df[df['Call_Category'] == 'SMS Sent'])
    total_calls = incoming_calls + outgoing_calls
    total_sms = sms_received + sms_sent
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    
    with col2:
        st.metric("Unique Contacts", f"{df['B_Party_Clean'].nunique():,}")
    
    with col3:
        st.metric("📞 Total Calls", f"{total_calls:,}", 
                 delta=f"{(total_calls/len(df)*100):.1f}% of records")
    
    with col4:
        st.metric("💬 Total SMS", f"{total_sms:,}",
                 delta=f"{(total_sms/len(df)*100):.1f}% of records")
    
    with col5:
        night_pct = (df['Is_Night'].sum() / len(df) * 100)
        st.metric("🌙 Night Activity", f"{night_pct:.1f}%", 
                 delta="High" if night_pct > 30 else "Normal",
                 delta_color="inverse" if night_pct > 30 else "normal")
    
    # Key metrics - Row 2: Detailed Breakdown
    st.markdown("#### 📊 Call & SMS Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📥 Incoming Calls", f"{incoming_calls:,}",
                 delta=f"{(incoming_calls/total_calls*100):.1f}% of calls" if total_calls > 0 else "0%")
    
    with col2:
        st.metric("📤 Outgoing Calls", f"{outgoing_calls:,}",
                 delta=f"{(outgoing_calls/total_calls*100):.1f}% of calls" if total_calls > 0 else "0%")
    
    with col3:
        st.metric("📨 SMS Received", f"{sms_received:,}",
                 delta=f"{(sms_received/total_sms*100):.1f}% of SMS" if total_sms > 0 else "0%")
    
    with col4:
        st.metric("📧 SMS Sent", f"{sms_sent:,}",
                 delta=f"{(sms_sent/total_sms*100):.1f}% of SMS" if total_sms > 0 else "0%")
    
    st.markdown("---")
    
    # ===== SANKEY DIAGRAM - CALL FLOW =====
    st.markdown("### 🌊 Communication Flow Analysis")
    st.caption("Visualize how communications flow between target and contacts")
    
    if total_calls > 0:
        # Get top 10 contacts for cleaner visualization
        calls_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])]
        top_contacts = calls_df['B_Party_Clean'].value_counts().head(10).index.tolist()
        
        # Filter for top contacts
        sankey_df = calls_df[calls_df['B_Party_Clean'].isin(top_contacts)]
        
        # Build Sankey data
        sources = []
        targets = []
        values = []
        colors = []
        
        # Incoming calls: Contact -> Target
        for contact in top_contacts:
            incoming = len(sankey_df[(sankey_df['B_Party_Clean'] == contact) & 
                                    (sankey_df['Call_Category'] == 'Incoming Call')])
            if incoming > 0:
                sources.append(contact)
                targets.append("📱 Target")
                values.append(incoming)
                colors.append('rgba(102, 126, 234, 0.4)')  # Blue for incoming
        
        # Outgoing calls: Target -> Contact
        for contact in top_contacts:
            outgoing = len(sankey_df[(sankey_df['B_Party_Clean'] == contact) & 
                                     (sankey_df['Call_Category'] == 'Outgoing Call')])
            if outgoing > 0:
                sources.append("📱 Target")
                targets.append(contact)
                values.append(outgoing)
                colors.append('rgba(245, 87, 108, 0.4)')  # Red for outgoing
        
        # Create node labels and colors
        all_nodes = ["📱 Target"] + top_contacts
        node_colors = ['#667eea'] + ['#764ba2'] * len(top_contacts)
        
        # Map to indices
        node_dict = {node: idx for idx, node in enumerate(all_nodes)}
        source_indices = [node_dict[s] for s in sources]
        target_indices = [node_dict[t] for t in targets]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="white", width=2),
                label=all_nodes,
                color=node_colors
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=colors
            )
        )])
        
        fig.update_layout(
            title="Call Flow: Top 10 Contacts (Blue=Incoming, Red=Outgoing)",
            font=dict(size=12, color='white'),
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call data available for flow visualization")
    
    # ===== SUNBURST CHART - CONTACT RELATIONSHIPS =====
    st.markdown("---")
    st.markdown("### ☀️ Contact Relationship Sunburst")
    st.caption("Hierarchical view of contacts by time period and frequency")
    
    if total_calls > 0:
        calls_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])].copy()
        
        # Categorize by time period
        calls_df['Time_Period'] = calls_df.apply(
            lambda x: 'Night' if x['Is_Night'] == 1 
            else 'Day' if x['Is_Day'] == 1 
            else 'Evening', axis=1
        )
        
        # Get top 15 contacts
        top_contacts = calls_df['B_Party_Clean'].value_counts().head(15).index
        sunburst_df = calls_df[calls_df['B_Party_Clean'].isin(top_contacts)]
        
        # Create sunburst data
        sunburst_data = []
        for period in ['Night', 'Day', 'Evening']:
            period_df = sunburst_df[sunburst_df['Time_Period'] == period]
            contact_counts = period_df['B_Party_Clean'].value_counts()
            
            for contact, count in contact_counts.items():
                # Categorize by frequency
                if count >= 20:
                    category = 'Very Frequent'
                elif count >= 10:
                    category = 'Frequent'
                elif count >= 5:
                    category = 'Moderate'
                else:
                    category = 'Occasional'
                
                sunburst_data.append({
                    'Time_Period': period,
                    'Category': category,
                    'Contact': contact[:15],  # Truncate for display
                    'Count': count
                })
        
        if sunburst_data:
            sunburst_df_plot = pd.DataFrame(sunburst_data)
            
            fig = px.sunburst(
                sunburst_df_plot,
                path=['Time_Period', 'Category', 'Contact'],
                values='Count',
                color='Count',
                color_continuous_scale='Purples',
                title="Contact Relationships by Time Period and Frequency"
            )
            
            fig.update_layout(
                template="plotly_dark",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call data available for sunburst visualization")

    
    # Activity overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Daily Activity Pattern")
        daily_counts = df.groupby(df['DateTime'].dt.date).size().reset_index()
        daily_counts.columns = ['Date', 'Count']
        
        fig = px.line(daily_counts, x='Date', y='Count',
                     title="Communication Activity Over Time",
                     template="plotly_dark")
        fig.update_traces(line_color='#667eea', line_width=3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🕐 Hourly Distribution")
        hourly_counts = df.groupby('Hour').size().reset_index()
        hourly_counts.columns = ['Hour', 'Count']
        
        fig = go.Figure(data=[
            go.Bar(x=hourly_counts['Hour'], y=hourly_counts['Count'],
                  marker_color='#764ba2')
        ])
        fig.update_layout(
            title="Activity by Hour of Day",
            xaxis_title="Hour",
            yaxis_title="Count",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Call and SMS breakdown with duration analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📞 Calls Breakdown")
        
        if total_calls > 0:
            call_data = pd.DataFrame({
                'Type': ['Incoming Calls', 'Outgoing Calls'],
                'Count': [incoming_calls, outgoing_calls]
            })
            
            fig = go.Figure(data=[
                go.Bar(
                    x=call_data['Type'], 
                    y=call_data['Count'],
                    marker_color=['#667eea', '#764ba2'],
                    text=call_data['Count'],
                    textposition='outside',
                    texttemplate='%{text:,}'
                )
            ])
            fig.update_layout(
                title="Incoming vs Outgoing Calls",
                xaxis_title="Call Type",
                yaxis_title="Count",
                template="plotly_dark",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No call data available")
    
    with col2:
        st.markdown("### 💬 SMS Breakdown")
        
        if total_sms > 0:
            sms_data = pd.DataFrame({
                'Type': ['SMS Received', 'SMS Sent'],
                'Count': [sms_received, sms_sent]
            })
            
            fig = go.Figure(data=[
                go.Bar(
                    x=sms_data['Type'], 
                    y=sms_data['Count'],
                    marker_color=['#f093fb', '#f5576c'],
                    text=sms_data['Count'],
                    textposition='outside',
                    texttemplate='%{text:,}'
                )
            ])
            fig.update_layout(
                title="Received vs Sent SMS",
                xaxis_title="SMS Type",
                yaxis_title="Count",
                template="plotly_dark",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No SMS data available")
    
    # Call Duration Analysis
    st.markdown("---")
    st.markdown("### ⏱️ Call Duration Analysis")
    
    if total_calls > 0:
        # Filter only calls with duration
        calls_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])].copy()
        incoming_df = calls_df[calls_df['Call_Category'] == 'Incoming Call']
        outgoing_df = calls_df[calls_df['Call_Category'] == 'Outgoing Call']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_incoming = incoming_df['Dur(s)'].mean() if len(incoming_df) > 0 else 0
            total_incoming_mins = incoming_df['Dur(s)'].sum() / 60 if len(incoming_df) > 0 else 0
            st.metric("📥 Avg Incoming Duration", 
                     f"{int(avg_incoming // 60)}m {int(avg_incoming % 60)}s",
                     delta=f"Total: {total_incoming_mins:.1f} mins")
        
        with col2:
            avg_outgoing = outgoing_df['Dur(s)'].mean() if len(outgoing_df) > 0 else 0
            total_outgoing_mins = outgoing_df['Dur(s)'].sum() / 60 if len(outgoing_df) > 0 else 0
            st.metric("📤 Avg Outgoing Duration", 
                     f"{int(avg_outgoing // 60)}m {int(avg_outgoing % 60)}s",
                     delta=f"Total: {total_outgoing_mins:.1f} mins")
        
        with col3:
            total_talk_time = calls_df['Dur(s)'].sum() / 3600  # Convert to hours
            avg_all_calls = calls_df['Dur(s)'].mean()
            st.metric("📊 Total Talk Time", 
                     f"{total_talk_time:.1f} hours",
                     delta=f"Avg: {int(avg_all_calls // 60)}m {int(avg_all_calls % 60)}s")
        
        # Duration distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Call Duration Distribution")
            
            # Create duration bins
            duration_bins = [0, 30, 60, 120, 300, 600, float('inf')]
            duration_labels = ['0-30s', '30s-1m', '1-2m', '2-5m', '5-10m', '10m+']
            calls_df['Duration_Bin'] = pd.cut(calls_df['Dur(s)'], bins=duration_bins, labels=duration_labels)
            
            duration_counts = calls_df['Duration_Bin'].value_counts().sort_index()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=duration_counts.index.astype(str), 
                    y=duration_counts.values,
                    marker_color='#667eea',
                    text=duration_counts.values,
                    textposition='outside'
                )
            ])
            fig.update_layout(
                title="Call Duration Distribution",
                xaxis_title="Duration Range",
                yaxis_title="Number of Calls",
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Incoming vs Outgoing Duration")
            
            duration_comparison = pd.DataFrame({
                'Call Type': ['Incoming', 'Outgoing'],
                'Average Duration (seconds)': [avg_incoming, avg_outgoing],
                'Total Duration (minutes)': [total_incoming_mins, total_outgoing_mins]
            })
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Average Duration', 'Total Duration'),
                specs=[[{'type': 'bar'}, {'type': 'bar'}]]
            )
            
            fig.add_trace(
                go.Bar(
                    x=duration_comparison['Call Type'],
                    y=duration_comparison['Average Duration (seconds)'],
                    marker_color=['#667eea', '#764ba2'],
                    text=duration_comparison['Average Duration (seconds)'].apply(lambda x: f"{int(x//60)}m {int(x%60)}s"),
                    textposition='outside',
                    showlegend=False
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=duration_comparison['Call Type'],
                    y=duration_comparison['Total Duration (minutes)'],
                    marker_color=['#667eea', '#764ba2'],
                    text=duration_comparison['Total Duration (minutes)'].apply(lambda x: f"{x:.1f}m"),
                    textposition='outside',
                    showlegend=False
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call duration data available")
    
    st.markdown("---")
    
    # Top Contacts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Top 10 Contacts (All)")
        top_contacts = df['B_Party_Clean'].value_counts().head(10)
        
        fig = go.Figure(data=[
            go.Bar(y=top_contacts.index, x=top_contacts.values,
                  orientation='h',
                  marker_color='#667eea')
        ])
        fig.update_layout(
            title="Most Frequent Contacts",
            xaxis_title="Number of Interactions",
            yaxis_title="Contact",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📞 Top 10 Call Contacts")
        
        if total_calls > 0:
            calls_only = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])]
            top_call_contacts = calls_only['B_Party_Clean'].value_counts().head(10)
            
            fig = go.Figure(data=[
                go.Bar(y=top_call_contacts.index, x=top_call_contacts.values,
                      orientation='h',
                      marker_color='#764ba2')
            ])
            fig.update_layout(
                title="Most Frequent Call Contacts",
                xaxis_title="Number of Calls",
                yaxis_title="Contact",
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No call data available")


def render_temporal_analysis(df, analyzer):
    """Render STATE-OF-THE-ART temporal analysis"""
    st.markdown("## 🌙 Advanced Temporal Analysis")
    st.caption("Comprehensive day/night pattern detection and suspicious activity identification")
    
    # Get temporal analysis
    temporal = analyzer.get_temporal_analysis()
    
    # Night vs Day Summary
    st.markdown("### 🌓 Night vs Day Activity Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        night_count = temporal['night_day_summary']['night_count']
        night_pct = temporal['night_day_summary']['night_percentage']
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #667eea;">{night_count:,}</h2>
            <p>Night Activities (22:00-06:00)</p>
            <h4>{night_pct:.1f}% of total</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        day_count = temporal['night_day_summary']['day_count']
        day_pct = temporal['night_day_summary']['day_percentage']
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #764ba2;">{day_count:,}</h2>
            <p>Day Activities (06:00-18:00)</p>
            <h4>{day_pct:.1f}% of total</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        evening_count = temporal['night_day_summary']['evening_count']
        evening_pct = temporal['night_day_summary']['evening_percentage']
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #f093fb;">{evening_count:,}</h2>
            <p>Evening Activities (18:00-22:00)</p>
            <h4>{evening_pct:.1f}% of total</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Suspicious patterns alert
    suspicious = temporal['suspicious_patterns']
    if suspicious['excessive_night_activity'] or suspicious['late_night_suspicious']:
        st.markdown(f"""
        <div class="alert-box">
            <h3>⚠️ Suspicious Temporal Patterns Detected</h3>
            <ul>
                <li><strong>Night Activity:</strong> {suspicious['night_activity_percentage']:.1f}% (Threshold: 30%)</li>
                <li><strong>Late Night (00:00-04:00):</strong> {suspicious['late_night_activity']} activities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed hourly heatmap
    st.markdown("### 📊 24-Hour Activity Heatmap")
    
    hourly_data = pd.DataFrame(list(temporal['hourly_distribution'].items()),
                               columns=['Hour', 'Count'])
    hourly_data['Hour'] = hourly_data['Hour'].astype(int)
    hourly_data = hourly_data.sort_values('Hour')
    
    # Create enhanced bar chart with color coding
    colors = []
    for hour in hourly_data['Hour']:
        if 0 <= hour < 6:
            colors.append('#ff4b4b')  # Late night - Red
        elif 6 <= hour < 12:
            colors.append('#ffa500')  # Morning - Orange
        elif 12 <= hour < 18:
            colors.append('#00cc00')  # Afternoon - Green
        elif 18 <= hour < 22:
            colors.append('#4b8bff')  # Evening - Blue
        else:
            colors.append('#ff1744')  # Night - Dark Red
    
    fig = go.Figure(data=[
        go.Bar(x=hourly_data['Hour'], y=hourly_data['Count'],
              marker_color=colors,
              text=hourly_data['Count'],
              textposition='outside')
    ])
    
    fig.update_layout(
        title="Activity Distribution Across 24 Hours",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Activities",
        template="plotly_dark",
        height=500,
        showlegend=False
    )
    
    # Add time period annotations
    fig.add_vrect(x0=-0.5, x1=5.5, fillcolor="red", opacity=0.1, line_width=0,
                 annotation_text="Late Night", annotation_position="top left")
    fig.add_vrect(x0=5.5, x1=11.5, fillcolor="orange", opacity=0.1, line_width=0,
                 annotation_text="Morning", annotation_position="top left")
    fig.add_vrect(x0=11.5, x1=17.5, fillcolor="green", opacity=0.1, line_width=0,
                 annotation_text="Afternoon", annotation_position="top left")
    fig.add_vrect(x0=17.5, x1=21.5, fillcolor="blue", opacity=0.1, line_width=0,
                 annotation_text="Evening", annotation_position="top left")
    fig.add_vrect(x0=21.5, x1=23.5, fillcolor="red", opacity=0.1, line_width=0,
                 annotation_text="Night", annotation_position="top left")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ===== CALENDAR HEATMAP & POLAR CHART =====
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Calendar Heatmap")
        st.caption("Activity intensity by day of month")
        
        # Prepare calendar data
        df['Date'] = df['DateTime'].dt.date
        df['Day'] = df['DateTime'].dt.day
        df['Month'] = df['DateTime'].dt.month
        df['Year'] = df['DateTime'].dt.year
        df['Weekday'] = df['DateTime'].dt.dayofweek
        
        # Get activity by date
        calendar_data = df.groupby(['Year', 'Month', 'Day']).size().reset_index(name='Count')
        calendar_data['Date'] = pd.to_datetime(calendar_data[['Year', 'Month', 'Day']])
        calendar_data['Weekday'] = calendar_data['Date'].dt.dayofweek
        calendar_data['Week'] = calendar_data['Date'].dt.isocalendar().week
        
        # Create heatmap
        if len(calendar_data) > 0:
            # Pivot for heatmap
            pivot_data = calendar_data.pivot_table(
                index='Weekday',
                columns='Week',
                values='Count',
                fill_value=0
            )
            
            weekday_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=weekday_labels,
                colorscale='Purples',
                hovertemplate='Week: %{x}\u003cbr\u003eDay: %{y}\u003cbr\u003eActivity: %{z}\u003cextra\u003e\u003c/extra\u003e'
            ))
            
            fig.update_layout(
                title="Activity Heatmap by Week and Day",
                xaxis_title="Week of Year",
                yaxis_title="Day of Week",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 24-Hour Activity Polar Chart")
        st.caption("Circular visualization of hourly patterns")
        
        # Prepare polar data
        hourly_counts = df.groupby('Hour').size().reset_index(name='Count')
        hourly_counts = hourly_counts.sort_values('Hour')
        
        # Create polar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=hourly_counts['Count'],
            theta=hourly_counts['Hour'] * 15,  # Convert to degrees (24 hours = 360 degrees)
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color='#667eea', width=3),
            name='Activity',
            hovertemplate='Hour: %{theta:.0f}°\u003cbr\u003eActivity: %{r}\u003cextra\u003e\u003c/extra\u003e'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    color='white'
                ),
                angularaxis=dict(
                    tickmode='array',
                    tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                    ticktext=['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
                    direction='clockwise',
                    rotation=90,
                    gridcolor='rgba(255,255,255,0.1)',
                    color='white'
                )
            ),
            title="24-Hour Activity Pattern",
            template="plotly_dark",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    # Night vs Day detailed comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌙 Night Activity Breakdown")
        night_data = temporal['night_activity']
        
        st.metric("Late Night (00:00-03:00)", f"{night_data['late_night_00_03']:,}")
        st.metric("Early Morning (03:00-06:00)", f"{night_data['late_night_03_06']:,}")
        st.metric("Night (22:00-00:00)", f"{night_data['night_22_00']:,}")
        
        st.markdown("**Top Night Contacts:**")
        for contact, count in list(night_data['top_night_contacts'].items())[:5]:
            st.text(f"• {contact}: {count} times")
        
        st.markdown(f"**Total Duration:** {night_data['night_duration_total']:,} seconds ({night_data['night_duration_total']/3600:.1f} hours)")
        st.markdown(f"**Average Duration:** {night_data['night_duration_avg']:.1f} seconds")
    
    with col2:
        st.markdown("### ☀️ Day Activity Breakdown")
        day_data = temporal['day_activity']
        
        st.metric("Morning (06:00-09:00)", f"{day_data['morning_06_09']:,}")
        st.metric("Mid-Morning (09:00-12:00)", f"{day_data['morning_09_12']:,}")
        st.metric("Afternoon (12:00-15:00)", f"{day_data['afternoon_12_15']:,}")
        st.metric("Late Afternoon (15:00-18:00)", f"{day_data['afternoon_15_18']:,}")
        
        st.markdown("**Top Day Contacts:**")
        for contact, count in list(day_data['top_day_contacts'].items())[:5]:
            st.text(f"• {contact}: {count} times")
        
        st.markdown(f"**Total Duration:** {day_data['day_duration_total']:,} seconds ({day_data['day_duration_total']/3600:.1f} hours)")
        st.markdown(f"**Average Duration:** {day_data['day_duration_avg']:.1f} seconds")
    
    # ===== CALL-FOCUSED TEMPORAL ANALYSIS =====
    st.markdown("---")
    st.markdown("### 📞 Call Patterns by Time Period")
    st.caption("Understanding **who** is being called during different times is critical for investigations")
    
    # Filter for calls only
    calls_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])].copy()
    
    if len(calls_df) > 0:
        # Separate by time period
        night_calls = calls_df[calls_df['Is_Night'] == 1]
        day_calls = calls_df[calls_df['Is_Day'] == 1]
        evening_calls = calls_df[calls_df['Is_Evening'] == 1]
        
        # Calculate metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            night_incoming = len(night_calls[night_calls['Call_Category'] == 'Incoming Call'])
            night_outgoing = len(night_calls[night_calls['Call_Category'] == 'Outgoing Call'])
            st.metric("🌙 Night Calls", f"{len(night_calls):,}",
                     delta=f"In: {night_incoming} | Out: {night_outgoing}")
        
        with col2:
            day_incoming = len(day_calls[day_calls['Call_Category'] == 'Incoming Call'])
            day_outgoing = len(day_calls[day_calls['Call_Category'] == 'Outgoing Call'])
            st.metric("☀️ Day Calls", f"{len(day_calls):,}",
                     delta=f"In: {day_incoming} | Out: {day_outgoing}")
        
        with col3:
            evening_incoming = len(evening_calls[evening_calls['Call_Category'] == 'Incoming Call'])
            evening_outgoing = len(evening_calls[evening_calls['Call_Category'] == 'Outgoing Call'])
            st.metric("🌆 Evening Calls", f"{len(evening_calls):,}",
                     delta=f"In: {evening_incoming} | Out: {evening_outgoing}")
        
        # Top Call Contacts by Time Period
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌙 Top Night Call Contacts")
            
            if len(night_calls) > 0:
                night_contacts = night_calls['B_Party_Clean'].value_counts().head(10)
                
                # Create detailed table
                night_contact_details = []
                for contact in night_contacts.index[:10]:
                    contact_calls = night_calls[night_calls['B_Party_Clean'] == contact]
                    incoming = len(contact_calls[contact_calls['Call_Category'] == 'Incoming Call'])
                    outgoing = len(contact_calls[contact_calls['Call_Category'] == 'Outgoing Call'])
                    avg_duration = contact_calls['Dur(s)'].mean()
                    
                    night_contact_details.append({
                        'Contact': contact,
                        'Total': len(contact_calls),
                        'In': incoming,
                        'Out': outgoing,
                        'Avg Duration': f"{int(avg_duration//60)}m {int(avg_duration%60)}s"
                    })
                
                night_df = pd.DataFrame(night_contact_details)
                st.dataframe(night_df, use_container_width=True, hide_index=True)
                
                # Visualization
                fig = go.Figure(data=[
                    go.Bar(
                        y=night_contacts.index[:10],
                        x=night_contacts.values[:10],
                        orientation='h',
                        marker_color='#667eea',
                        text=night_contacts.values[:10],
                        textposition='outside'
                    )
                ])
                fig.update_layout(
                    title="Night Call Frequency",
                    xaxis_title="Number of Calls",
                    yaxis_title="Contact",
                    template="plotly_dark",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No night calls found")
        
        with col2:
            st.markdown("#### ☀️ Top Day Call Contacts")
            
            if len(day_calls) > 0:
                day_contacts = day_calls['B_Party_Clean'].value_counts().head(10)
                
                # Create detailed table
                day_contact_details = []
                for contact in day_contacts.index[:10]:
                    contact_calls = day_calls[day_calls['B_Party_Clean'] == contact]
                    incoming = len(contact_calls[contact_calls['Call_Category'] == 'Incoming Call'])
                    outgoing = len(contact_calls[contact_calls['Call_Category'] == 'Outgoing Call'])
                    avg_duration = contact_calls['Dur(s)'].mean()
                    
                    day_contact_details.append({
                        'Contact': contact,
                        'Total': len(contact_calls),
                        'In': incoming,
                        'Out': outgoing,
                        'Avg Duration': f"{int(avg_duration//60)}m {int(avg_duration%60)}s"
                    })
                
                day_df = pd.DataFrame(day_contact_details)
                st.dataframe(day_df, use_container_width=True, hide_index=True)
                
                # Visualization
                fig = go.Figure(data=[
                    go.Bar(
                        y=day_contacts.index[:10],
                        x=day_contacts.values[:10],
                        orientation='h',
                        marker_color='#764ba2',
                        text=day_contacts.values[:10],
                        textposition='outside'
                    )
                ])
                fig.update_layout(
                    title="Day Call Frequency",
                    xaxis_title="Number of Calls",
                    yaxis_title="Contact",
                    template="plotly_dark",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No day calls found")
        
        # Call Duration Comparison by Time Period
        st.markdown("#### ⏱️ Call Duration by Time Period")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average duration comparison
            time_duration_data = pd.DataFrame({
                'Time Period': ['Night', 'Day', 'Evening'],
                'Avg Duration (s)': [
                    night_calls['Dur(s)'].mean() if len(night_calls) > 0 else 0,
                    day_calls['Dur(s)'].mean() if len(day_calls) > 0 else 0,
                    evening_calls['Dur(s)'].mean() if len(evening_calls) > 0 else 0
                ],
                'Total Calls': [len(night_calls), len(day_calls), len(evening_calls)]
            })
            
            fig = go.Figure(data=[
                go.Bar(
                    x=time_duration_data['Time Period'],
                    y=time_duration_data['Avg Duration (s)'],
                    marker_color=['#667eea', '#764ba2', '#f093fb'],
                    text=time_duration_data['Avg Duration (s)'].apply(lambda x: f"{int(x//60)}m {int(x%60)}s"),
                    textposition='outside'
                )
            ])
            fig.update_layout(
                title="Average Call Duration by Time",
                xaxis_title="Time Period",
                yaxis_title="Average Duration (seconds)",
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Incoming vs Outgoing by time
            time_direction_data = pd.DataFrame({
                'Time Period': ['Night', 'Night', 'Day', 'Day', 'Evening', 'Evening'],
                'Direction': ['Incoming', 'Outgoing', 'Incoming', 'Outgoing', 'Incoming', 'Outgoing'],
                'Count': [
                    night_incoming, night_outgoing,
                    day_incoming, day_outgoing,
                    evening_incoming, evening_outgoing
                ]
            })
            
            fig = px.bar(
                time_direction_data,
                x='Time Period',
                y='Count',
                color='Direction',
                barmode='group',
                color_discrete_map={'Incoming': '#667eea', 'Outgoing': '#f5576c'},
                template="plotly_dark",
                title="Incoming vs Outgoing Calls by Time"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call data available for temporal analysis")
    
    # ===== END CALL-FOCUSED ANALYSIS =====
    
    
    # Burst activity detection
    st.markdown("---")
    st.markdown("### 🔥 Burst Activity Detection")
    st.caption("Periods of unusually high activity (> mean + 2σ)")
    
    comm_patterns = analyzer.get_communication_patterns()
    bursts = comm_patterns.get('burst_activity', [])
    
    if bursts:
        burst_df = pd.DataFrame(bursts[:10])
        burst_df['datetime'] = burst_df['date'] + ' ' + burst_df['hour'].astype(str) + ':00'
        
        fig = go.Figure(data=[
            go.Bar(x=burst_df['datetime'], y=burst_df['count'],
                  marker_color='#ff4b4b',
                  text=burst_df['count'],
                  textposition='outside')
        ])
        
        fig.add_hline(y=burst_df['threshold'].iloc[0], line_dash="dash",
                     line_color="yellow",
                     annotation_text="Threshold")
        
        fig.update_layout(
            title="Top 10 Burst Activity Periods",
            xaxis_title="Date & Hour",
            yaxis_title="Activity Count",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No significant burst activity detected")


def render_contact_network(df, analyzer):
    """Render contact network analysis"""
    st.markdown("## 👥 Contact Network Analysis")
    
    network_analyzer = NetworkAnalyzer(df)
    contact_analysis = analyzer.get_contact_analysis()
    
    # Contact summary
    col1, col2, col3, col4 = st.columns(4)
    
    freq = contact_analysis['contact_frequency']
    with col1:
        st.metric("Unique Contacts", f"{freq['unique_contacts']:,}")
    with col2:
        st.metric("One-time Contacts", f"{freq['one_time_contacts']:,}")
    with col3:
        st.metric("Frequent (5+)", f"{freq['frequent_contacts_5plus']:,}")
    with col4:
        st.metric("Very Frequent (10+)", f"{freq['very_frequent_10plus']:,}")
    
    st.markdown("---")
    
    # Contact clustering
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Contact Clusters")
        clusters = network_analyzer.cluster_contacts()
        
        cluster_summary = {
            'Very Frequent (20+)': len(clusters['very_frequent']),
            'Frequent (10-19)': len(clusters['frequent']),
            'Moderate (5-9)': len(clusters['moderate']),
            'Occasional (2-4)': len(clusters['occasional']),
            'One-time': len(clusters['one_time'])
        }
        
        fig = px.pie(values=list(cluster_summary.values()),
                    names=list(cluster_summary.keys()),
                    title="Contact Distribution by Frequency",
                    color_discrete_sequence=px.colors.sequential.Purples_r,
                    template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔝 Top 15 Contacts")
        top_contacts = pd.DataFrame(list(contact_analysis['top_contacts'].items())[:15],
                                    columns=['Contact', 'Count'])
        
        fig = go.Figure(data=[
            go.Bar(y=top_contacts['Contact'], x=top_contacts['Count'],
                  orientation='h',
                  marker_color='#667eea',
                  text=top_contacts['Count'],
                  textposition='outside')
        ])
        fig.update_layout(
            title="Most Frequent Contacts",
            xaxis_title="Interactions",
            yaxis_title="Contact",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== NETWORK GRAPH - 2D/3D TOGGLE =====
    st.markdown("### 🕸️ Contact Network Visualization")
    
    min_interactions = st.slider("Minimum interactions to display", 1, 20, 5)
    
    G = network_analyzer.build_network_graph(min_interactions=min_interactions)
    
    if G.number_of_nodes() > 1:
        # Show 2D version by default
        st.caption("📊 2D Network View (Click below to expand to 3D)")
        
        # Create 2D network visualization
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                          mode='lines',
                          line=dict(width=1, color='rgba(0, 245, 255, 0.3)'),
                          hoverinfo='none',
                          showlegend=False)
            )
        
        node_colors = ['#ff4b4b' if G.nodes[node].get('node_type') == 'target' else '#00f5ff' 
                      for node in G.nodes()]
        
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                size=[G.nodes[node].get('size', 10) for node in G.nodes()],
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=[node[:10] for node in G.nodes()],
            textposition="top center",
            textfont=dict(color='white', size=8),
            hovertext=[f"{node}\u003cbr\u003eConnections: {G.degree(node)}" for node in G.nodes()],
            showlegend=False
        )
        
        fig_2d = go.Figure(data=edge_trace + [node_trace])
        fig_2d.update_layout(
            title=f"2D Network ({G.number_of_nodes()} nodes)",
            showlegend=False,
            template="plotly_dark",
            height=400,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_2d, use_container_width=True)
        
        # Expandable 3D version
        with st.expander("🌐 **Expand to 3D Interactive View** (Rotate, Zoom, Explore)", expanded=False):
            st.caption("Fully interactive 3D network - drag to rotate, scroll to zoom")
            
            # Create 3D network visualization
            pos_3d = nx.spring_layout(G, dim=3, k=0.5, iterations=50)
            
            # Extract 3D coordinates
            x_nodes = [pos_3d[node][0] for node in G.nodes()]
            y_nodes = [pos_3d[node][1] for node in G.nodes()]
            z_nodes = [pos_3d[node][2] for node in G.nodes()]
            
            # Create edges in 3D
            edge_x = []
            edge_y = []
            edge_z = []
            
            for edge in G.edges():
                x0, y0, z0 = pos_3d[edge[0]]
                x1, y1, z1 = pos_3d[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_z.extend([z0, z1, None])
            
            # Create edge trace with neon glow
            edge_trace_3d = go.Scatter3d(
                x=edge_x, y=edge_y, z=edge_z,
                mode='lines',
                line=dict(color='rgba(0, 245, 255, 0.3)', width=2),
                hoverinfo='none',
                showlegend=False
            )
            
            # Node colors and sizes
            node_colors_3d = []
            node_sizes_3d = []
            node_text_3d = []
            
            for node in G.nodes():
                if G.nodes[node].get('node_type') == 'target':
                    node_colors_3d.append('#ff4b4b')  # Red for target
                    node_sizes_3d.append(20)
                else:
                    node_colors_3d.append('#00f5ff')  # Cyan for contacts
                    node_sizes_3d.append(G.nodes[node].get('size', 10))
                node_text_3d.append(f"{node[:15]}\u003cbr\u003eConnections: {G.degree(node)}")
            
            # Create node trace with glow effect
            node_trace_3d = go.Scatter3d(
                x=x_nodes, y=y_nodes, z=z_nodes,
                mode='markers+text',
                marker=dict(
                    size=node_sizes_3d,
                    color=node_colors_3d,
                    line=dict(color='white', width=2),
                    opacity=0.9
                ),
                text=[node[:10] for node in G.nodes()],
                textposition='top center',
                textfont=dict(color='white', size=10),
                hovertext=node_text_3d,
                hoverinfo='text',
                showlegend=False
            )
            
            # Create 3D figure
            fig_3d = go.Figure(data=[edge_trace_3d, node_trace_3d])
            
            fig_3d.update_layout(
                title=f"🌐 3D Contact Network ({G.number_of_nodes()} nodes) - Drag to Rotate",
                showlegend=False,
                template="plotly_dark",
                height=700,
                scene=dict(
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
                    zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
                    bgcolor='rgba(0,0,0,0)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.info("Increase minimum interactions to see network graph")
    
    # ===== CALL-FOCUSED CONTACT NETWORK =====
    st.markdown("---")
    st.markdown("### 📞 Call Contact Analysis by Time Period")
    st.caption("Identifying **who** is being called during different times helps reveal suspicious patterns")
    
    # Filter for calls only
    calls_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])].copy()
    
    if len(calls_df) > 0:
        # Time-based contact clustering
        night_calls = calls_df[calls_df['Is_Night'] == 1]
        day_calls = calls_df[calls_df['Is_Day'] == 1]
        
        # Get unique contacts by time
        night_contacts_set = set(night_calls['B_Party_Clean'].unique())
        day_contacts_set = set(day_calls['B_Party_Clean'].unique())
        
        # Categorize contacts
        night_only = night_contacts_set - day_contacts_set
        day_only = day_contacts_set - night_contacts_set
        both_times = night_contacts_set & day_contacts_set
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌙 Night-Only Contacts", f"{len(night_only):,}",
                     delta="Only called at night",
                     delta_color="inverse" if len(night_only) > 0 else "off")
        
        with col2:
            st.metric("☀️ Day-Only Contacts", f"{len(day_only):,}",
                     delta="Only called during day")
        
        with col3:
            st.metric("🔄 Both Times", f"{len(both_times):,}",
                     delta="Called day & night")
        
        with col4:
            total_call_contacts = len(calls_df['B_Party_Clean'].unique())
            st.metric("📞 Total Call Contacts", f"{total_call_contacts:,}")
        
        # Visualize contact distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Contact Time Distribution")
            
            time_dist_data = pd.DataFrame({
                'Category': ['Night Only', 'Day Only', 'Both Times'],
                'Count': [len(night_only), len(day_only), len(both_times)]
            })
            
            fig = px.pie(
                time_dist_data,
                values='Count',
                names='Category',
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'],
                template="plotly_dark",
                title="Contact Distribution by Time Pattern"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Suspicious Night-Only Contacts")
            
            if len(night_only) > 0:
                # Get details for night-only contacts
                night_only_details = []
                for contact in list(night_only)[:10]:
                    contact_calls = night_calls[night_calls['B_Party_Clean'] == contact]
                    incoming = len(contact_calls[contact_calls['Call_Category'] == 'Incoming Call'])
                    outgoing = len(contact_calls[contact_calls['Call_Category'] == 'Outgoing Call'])
                    avg_duration = contact_calls['Dur(s)'].mean()
                    
                    night_only_details.append({
                        'Contact': contact,
                        'Calls': len(contact_calls),
                        'In': incoming,
                        'Out': outgoing,
                        'Avg Duration': f"{int(avg_duration//60)}m {int(avg_duration%60)}s"
                    })
                
                night_only_df = pd.DataFrame(night_only_details)
                st.dataframe(night_only_df, use_container_width=True, hide_index=True)
                
                st.caption("⚠️ These contacts are **only** called at night (22:00-06:00) - potentially suspicious")
            else:
                st.info("No night-only contacts found")
        
        # Contact frequency heatmap by time
        st.markdown("#### 📊 Contact Activity Heatmap")
        
        # Get top 15 call contacts
        top_call_contacts = calls_df['B_Party_Clean'].value_counts().head(15).index
        
        # Create hourly activity matrix
        heatmap_data = []
        for contact in top_call_contacts:
            contact_calls = calls_df[calls_df['B_Party_Clean'] == contact]
            hourly_counts = contact_calls.groupby('Hour').size()
            
            # Fill in missing hours with 0
            hour_data = [hourly_counts.get(h, 0) for h in range(24)]
            heatmap_data.append(hour_data)
        
        if heatmap_data:
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=list(range(24)),
                y=[str(c)[:15] for c in top_call_contacts],
                colorscale='Purples',
                hovertemplate='Contact: %{y}\u003cbr\u003eHour: %{x}:00\u003cbr\u003eCalls: %{z}\u003cextra\u003e\u003c/extra\u003e'
            ))
            
            fig.update_layout(
                title="Top 15 Call Contacts - Activity by Hour of Day",
                xaxis_title="Hour of Day",
                yaxis_title="Contact",
                template="plotly_dark",
                height=500
            )
            
            # Add time period markers
            fig.add_vrect(x0=-0.5, x1=5.5, fillcolor="red", opacity=0.1, line_width=0)
            fig.add_vrect(x0=21.5, x1=23.5, fillcolor="red", opacity=0.1, line_width=0)
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🔴 Red zones indicate night hours (22:00-06:00)")
    else:
        st.info("No call data available for contact network analysis")
    
    # ===== END CALL-FOCUSED CONTACT NETWORK =====



def render_location_intelligence(df, analyzer):
    """Render location intelligence"""
    st.markdown("## 🗺️ Location Intelligence")
    
    location_analyzer = LocationAnalyzer(df)
    location_analysis = analyzer.get_location_analysis()
    
    if 'error' in location_analysis:
        st.warning(location_analysis['error'])
        return
    
    # Location summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Unique Towers", f"{location_analysis['unique_towers']:,}")
    with col2:
        st.metric("Night Locations", f"{location_analysis['night_locations']:,}")
    with col3:
        st.metric("Day Locations", f"{location_analysis['day_locations']:,}")
    
    st.markdown("---")
    
    # ===== CELL TOWER DATABASE LOOKUP =====
    st.markdown("### 📡 Cell Tower Database Lookup")
    st.caption("Lookup cell tower locations from Cell ID using open-source databases")
    
    # Import cell tower database
    from cell_tower_db import CellTowerDatabase
    
    # Initialize database
    if 'cell_tower_db' not in st.session_state:
        st.session_state.cell_tower_db = CellTowerDatabase()
    
    cell_db = st.session_state.cell_tower_db
    
    # Show database info
    with st.expander("📚 Available Databases", expanded=False):
        db_info = cell_db.get_database_info()
        
        for db_key, info in db_info.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{info['name']}**")
                st.caption(f"🌐 {info['url']}")
                st.caption(f"📊 Coverage: {info['coverage']} | Rate Limit: {info['rate_limit']}")
            
            with col2:
                if info['status'] == 'Available':
                    st.success("✅ Active")
                else:
                    st.warning("⚠️ " + info['status'])
            
            st.markdown("---")
    
    # Cell tower enrichment option
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("💡 **Tip**: Cell tower lookup uses free Mozilla Location Service API (no API key required)")
    
    with col2:
        if st.button("🔍 Lookup Cell Towers", type="primary"):
            with st.spinner("Looking up cell tower locations..."):
                try:
                    # Enrich dataframe with cell tower data
                    enriched_df = cell_db.enrich_cdr_with_cell_towers(df)
                    
                    # Count successful lookups
                    successful = enriched_df['Cell_Tower_Lat'].notna().sum()
                    total = len(enriched_df['First CGI'].dropna().unique())
                    
                    if successful > 0:
                        st.session_state.enriched_df = enriched_df
                        st.success(f"✅ Found {successful}/{total} cell tower locations!")
                        
                        # Show comparison
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("GPS Coordinates", f"{df['First_Lat'].notna().sum():,}")
                        with col_b:
                            st.metric("Cell Tower Locations", f"{successful:,}")
                    else:
                        st.warning("No cell tower locations found. This may be due to:")
                        st.markdown("- Cell IDs not in database")
                        st.markdown("- API rate limits")
                        st.markdown("- Network connectivity issues")
                        
                except Exception as e:
                    st.error(f"Error during lookup: {str(e)}")
    
    # Show enriched data if available
    if 'enriched_df' in st.session_state:
        enriched_df = st.session_state.enriched_df
        
        st.markdown("#### 📊 Cell Tower vs GPS Comparison")
        
        # Sample comparison table
        comparison_df = enriched_df[enriched_df['Cell_Tower_Lat'].notna()].head(10)[[
            'DateTime', 'First CGI', 'First_Lat', 'First_Long', 
            'Cell_Tower_Lat', 'Cell_Tower_Long'
        ]].copy()
        
        # Calculate distance between GPS and Cell Tower
        loc_analyzer = LocationAnalyzer(df)
        
        comparison_df['Distance_km'] = comparison_df.apply(
            lambda row: loc_analyzer.calculate_distance(
                row['First_Lat'], row['First_Long'],
                row['Cell_Tower_Lat'], row['Cell_Tower_Long']
            ) if pd.notna(row['Cell_Tower_Lat']) else None,
            axis=1
        )
        
        st.dataframe(comparison_df, use_container_width=True)
        
        avg_distance = comparison_df['Distance_km'].mean()
        st.caption(f"📏 Average distance between GPS and Cell Tower: {avg_distance:.2f} km")
    
    # ===== END OF CELL TOWER LOOKUP =====
    
    st.markdown("---")
    
    # Map visualization
    st.markdown("### 🗺️ Tower Location Map")
    
    # Add communication type filter
    col1, col2 = st.columns([1, 2])
    with col1:
        comm_filter = st.radio("Communication Type:", ["All", "Calls Only", "SMS Only"], horizontal=False)
    with col2:
        time_filter = st.radio("Filter by time:", ["All", "Night", "Day", "Evening"], horizontal=True)
    
    # Apply communication type filter first
    if comm_filter == "Calls Only":
        filtered_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])]
    elif comm_filter == "SMS Only":
        filtered_df = df[df['Call_Category'].isin(['SMS Received', 'SMS Sent'])]
    else:
        filtered_df = df
    
    # Get appropriate locations based on time filter
    if time_filter == "All":
        map_df = filtered_df.dropna(subset=['First_Lat', 'First_Long'])
    elif time_filter == "Night":
        map_df = filtered_df[filtered_df['Is_Night'] == 1].dropna(subset=['First_Lat', 'First_Long'])
    elif time_filter == "Day":
        map_df = filtered_df[filtered_df['Is_Day'] == 1].dropna(subset=['First_Lat', 'First_Long'])
    else:
        map_df = filtered_df[filtered_df['Is_Evening'] == 1].dropna(subset=['First_Lat', 'First_Long'])
    
    if len(map_df) > 0:
        # Create folium map
        center_lat = map_df['First_Lat'].mean()
        center_lon = map_df['First_Long'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add markers for top locations
        location_counts = map_df.groupby(['First_Lat', 'First_Long']).size().reset_index()
        location_counts.columns = ['lat', 'lon', 'count']
        location_counts = location_counts.nlargest(50, 'count')
        
        for _, row in location_counts.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=min(row['count'] / 2, 20),
                popup=f"Count: {row['count']}",
                color='red' if time_filter == 'Night' else 'blue',
                fill=True,
                fillOpacity=0.6
            ).add_to(m)
        
        folium_static(m, width=1200, height=600)
    else:
        st.info("No location data available for selected filter")
    
    # ===== ANIMATED MOVEMENT TIMELINE WITH REVERSE GEOCODING =====
    st.markdown("---")
    st.markdown("### 🎬 Movement Timeline (Animated)")
    st.caption("Watch the suspect's movement over time - each frame shows chronological location with address")
    
    # Filter by call type
    st.markdown("#### 📞 Filter by Communication Type")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_calls = st.checkbox("📞 Voice Calls", value=True, key="timeline_calls")
    with col2:
        show_sms = st.checkbox("💬 SMS", value=True, key="timeline_sms")
    with col3:
        show_incoming = st.checkbox("📥 Incoming", value=True, key="timeline_in")
    with col4:
        show_outgoing = st.checkbox("📤 Outgoing", value=True, key="timeline_out")
    
    # Get data with valid coordinates sorted by time
    movement_df = df.dropna(subset=['First_Lat', 'First_Long']).sort_values('DateTime').copy()
    
    # Apply call type filters
    call_type_filter = []
    if show_calls:
        call_type_filter.extend(['Incoming Call', 'Outgoing Call'])
    if show_sms:
        call_type_filter.extend(['SMS Received', 'SMS Sent'])
    
    if call_type_filter:
        movement_df = movement_df[movement_df['Call_Category'].isin(call_type_filter)]
    
    # Apply direction filters
    if not show_incoming:
        movement_df = movement_df[~movement_df['Call_Category'].isin(['Incoming Call', 'SMS Received'])]
    if not show_outgoing:
        movement_df = movement_df[~movement_df['Call_Category'].isin(['Outgoing Call', 'SMS Sent'])]
    
    if len(movement_df) > 0:
        # Prepare data for animation
        movement_df['DateTimeStr'] = movement_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        movement_df['Date'] = movement_df['DateTime'].dt.strftime('%Y-%m-%d')
        movement_df['Time'] = movement_df['DateTime'].dt.strftime('%H:%M:%S')
        movement_df['Sequence'] = range(1, len(movement_df) + 1)
        
        # Add time period color
        def get_time_color(hour):
            if 0 <= hour < 6:
                return 'Late Night'
            elif 6 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 18:
                return 'Afternoon'
            elif 18 <= hour < 22:
                return 'Evening'
            else:
                return 'Night'
        
        movement_df['TimePeriodColor'] = movement_df['Hour'].apply(get_time_color)
        
        # Add sequence number for animation
        movement_df = movement_df.sort_values('DateTime').reset_index(drop=True)
        movement_df['Sequence'] = range(len(movement_df))
        movement_df['DateTimeStr'] = movement_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Option to show only major movements (city-to-city)
        show_major_only = st.checkbox(
            "🏙️ Show Major Movements Only (City-to-City)",
            value=False,
            help="Filter out minor movements within the same area. Shows only significant location changes (>5km distance)."
        )
        
        # Store original count before filtering
        original_count = len(movement_df)
        
        if show_major_only:
            # Filter to show only major movements (use LocationAnalyzer from top import)
            loc_analyzer = LocationAnalyzer(movement_df)
            
            major_movements = [movement_df.iloc[0]]  # Always include first location
            
            for i in range(1, len(movement_df)):
                prev_lat = major_movements[-1]['First_Lat']
                prev_lon = major_movements[-1]['First_Long']
                curr_lat = movement_df.iloc[i]['First_Lat']
                curr_lon = movement_df.iloc[i]['First_Long']
                
                # Calculate distance from last major movement
                distance = loc_analyzer.calculate_distance(prev_lat, prev_lon, curr_lat, curr_lon)
                
                # Only include if moved more than 5km
                if distance > 5:
                    major_movements.append(movement_df.iloc[i])
            
            movement_df = pd.DataFrame(major_movements).reset_index(drop=True)
            movement_df['Sequence'] = range(len(movement_df))
            st.success(f"🏙️ Showing {len(movement_df)} major movements (filtered from {original_count} total events)")
        
        # Use ALL events or filtered major movements
        sample_df = movement_df.copy()
        
        st.info(f"📍 Showing all {len(sample_df)} movement events")
        
        # Option to enable reverse geocoding
        enable_geocoding = st.checkbox(
            "🌍 Enable Location Names (slower - fetches actual addresses)", 
            value=False,
            help="Uncheck for faster loading. Location names will show coordinates instead."
        )
        
        # Reverse geocoding for location names (optional)
        if enable_geocoding:
            st.write("🌍 Fetching location names...")
            progress_bar = st.progress(0)
            
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut, GeocoderServiceError
            import time
            
            geolocator = Nominatim(user_agent="cdr_analyzer_law_enforcement")
            
            def get_location_name(lat, lon, retry=3):
                """Get location name with retry logic"""
                for attempt in range(retry):
                    try:
                        location = geolocator.reverse(f"{lat}, {lon}", timeout=10, language='en')
                        if location:
                            address = location.raw.get('address', {})
                            # Build a readable address
                            parts = []
                            if 'suburb' in address:
                                parts.append(address['suburb'])
                            elif 'neighbourhood' in address:
                                parts.append(address['neighbourhood'])
                            elif 'village' in address:
                                parts.append(address['village'])
                            
                            if 'city' in address:
                                parts.append(address['city'])
                            elif 'town' in address:
                                parts.append(address['town'])
                            
                            if 'state' in address:
                                parts.append(address['state'])
                            
                            return ', '.join(parts) if parts else location.address[:50]
                        return f"Unknown ({lat:.4f}, {lon:.4f})"
                    except (GeocoderTimedOut, GeocoderServiceError):
                        if attempt < retry - 1:
                            time.sleep(1)
                        continue
                    except Exception:
                        return f"Location ({lat:.4f}, {lon:.4f})"
                return f"Location ({lat:.4f}, {lon:.4f})"
            
            # Get unique locations to minimize API calls
            unique_locs = sample_df[['First_Lat', 'First_Long']].drop_duplicates()
            location_cache = {}
            
            for idx, (_, row) in enumerate(unique_locs.iterrows()):
                lat, lon = row['First_Lat'], row['First_Long']
                key = f"{lat:.5f},{lon:.5f}"
                location_cache[key] = get_location_name(lat, lon)
                progress_bar.progress((idx + 1) / len(unique_locs))
                time.sleep(0.5)  # Rate limiting
            
            progress_bar.empty()
            
            # Apply location names to dataframe
            sample_df['Location'] = sample_df.apply(
                lambda row: location_cache.get(f"{row['First_Lat']:.5f},{row['First_Long']:.5f}", "Unknown"),
                axis=1
            )
        else:
            # Use coordinates as location (fast)
            sample_df['Location'] = sample_df.apply(
                lambda row: f"{row['First_Lat']:.4f}, {row['First_Long']:.4f}",
                axis=1
            )
        
        # Animation speed control
        st.markdown("#### ⚡ Animation Speed")
        speed_option = st.radio(
            "Select animation speed:",
            options=["1x (Normal)", "2x (Fast)", "3x (Faster)", "4x (Fastest)"],
            horizontal=True,
            index=0,
            key="anim_speed"
        )
        
        # Extract speed multiplier
        speed_map = {"1x (Normal)": 1000, "2x (Fast)": 500, "3x (Faster)": 333, "4x (Fastest)": 250}
        frame_duration = speed_map[speed_option]
        
        # Create animated scatter mapbox with LARGE markers
        fig = px.scatter_mapbox(
            sample_df,
            lat='First_Lat',
            lon='First_Long',
            animation_frame='Sequence',
            color='TimePeriodColor',
            size=[30] * len(sample_df),  # Large constant size for all markers
            hover_name='Location',
            hover_data={
                'DateTimeStr': True,
                'First_Lat': ':.5f',
                'First_Long': ':.5f',
                'B_Party_Clean': True,
                'Call_Category': True,
                'TimePeriodColor': True,
                'Sequence': False,
                'Location': True
            },
            color_discrete_map={
                'Late Night': '#ff4b4b',
                'Morning': '#ffa500',
                'Afternoon': '#00cc00',
                'Evening': '#4b8bff',
                'Night': '#ff1744'
            },
            zoom=10,
            height=700,
            title="🎬 Chronological Movement Pattern - Large Markers with Path Trail"
        )
        
        # IMPORTANT: Add path BEFORE the scatter so markers appear on top
        # Move the animated scatter trace to the front
        if len(fig.data) > 0:
            # The px.scatter_mapbox creates the first trace (animated markers)
            # We need to add the path trail and then reorder
            pass
        
        # Add THICK movement path line to show complete trajectory (will be behind markers)
        fig.add_trace(go.Scattermapbox(
            lat=sample_df['First_Lat'],
            lon=sample_df['First_Long'],
            mode='lines+markers',
            line=dict(width=4, color='rgba(150, 150, 150, 0.4)'),  # Gray trail
            marker=dict(size=8, color='rgba(200, 200, 200, 0.6)'),  # Small gray dots for visited
            name='Visited Path',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # Reorder traces so animated markers are on top
        if len(fig.data) >= 2:
            # Move the first trace (animated markers) to the end so it renders on top
            fig.data = (fig.data[1],) + (fig.data[0],)
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(
                    lat=sample_df['First_Lat'].mean(),
                    lon=sample_df['First_Long'].mean()
                ),
                zoom=11
            ),
            template="plotly_dark",
            showlegend=True,
            legend=dict(
                title="Time Period",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # Enable all map interactions
            dragmode='zoom',
            hovermode='closest'
        )
        
        # Update animation settings with date/time labels
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = frame_duration
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = frame_duration // 2
        
        # Update slider to show date/time instead of sequence number
        if hasattr(fig.layout, 'sliders') and len(fig.layout.sliders) > 0:
            for i, frame in enumerate(fig.frames):
                if i < len(sample_df):
                    # Get the actual date/time for this frame
                    datetime_str = sample_df.iloc[i]['DateTimeStr']
                    fig.layout.sliders[0].steps[i]['label'] = datetime_str
        
        # Display with full interactivity enabled
        st.plotly_chart(fig, use_container_width=True, config={
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
        })
        
        # Movement statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Movements Tracked", f"{len(movement_df):,}")
        
        with col2:
            time_span = (movement_df['DateTime'].max() - movement_df['DateTime'].min()).days
            st.metric("Time Span", f"{time_span} days")
        
        with col3:
            # Calculate approximate distance traveled
            if len(movement_df) > 1:
                loc_analyzer = LocationAnalyzer(df)
                total_dist = 0
                for i in range(len(movement_df) - 1):
                    lat1 = movement_df.iloc[i]['First_Lat']
                    lon1 = movement_df.iloc[i]['First_Long']
                    lat2 = movement_df.iloc[i+1]['First_Lat']
                    lon2 = movement_df.iloc[i+1]['First_Long']
                    total_dist += loc_analyzer.calculate_distance(lat1, lon1, lat2, lon2)
                st.metric("Approx. Distance", f"{total_dist:.1f} km")
            else:
                st.metric("Approx. Distance", "N/A")
        
        # Timeline breakdown by time period
        st.markdown("#### 📊 Movement by Time Period")
        period_counts = movement_df['TimePeriodColor'].value_counts()
        
        fig_period = go.Figure(data=[
            go.Bar(
                x=period_counts.index,
                y=period_counts.values,
                marker_color=['#ff4b4b' if p == 'Late Night' else 
                             '#ffa500' if p == 'Morning' else 
                             '#00cc00' if p == 'Afternoon' else 
                             '#4b8bff' if p == 'Evening' else '#ff1744' 
                             for p in period_counts.index],
                text=period_counts.values,
                textposition='outside'
            )
        ])
        
        fig_period.update_layout(
            title="Movement Events by Time Period",
            xaxis_title="Time Period",
            yaxis_title="Number of Events",
            template="plotly_dark",
            height=350
        )
        
        st.plotly_chart(fig_period, use_container_width=True)
        
        # Most visited locations with names
        st.markdown("#### 📍 Most Visited Locations")
        if 'Location' in sample_df.columns:
            location_visits = sample_df['Location'].value_counts().head(10)
            
            fig_visits = go.Figure(data=[
                go.Bar(
                    y=location_visits.index,
                    x=location_visits.values,
                    orientation='h',
                    marker_color='#667eea',
                    text=location_visits.values,
                    textposition='outside'
                )
            ])
            
            fig_visits.update_layout(
                title="Top 10 Most Visited Locations",
                xaxis_title="Number of Visits",
                yaxis_title="Location",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig_visits, use_container_width=True)
        
    else:
        st.info("No location data available for movement timeline")
    # ===== END OF ANIMATED TIMELINE =====
    
    # Top locations table
    st.markdown("---")
    st.markdown("### 📍 Top 10 Locations")
    
    if location_analysis['top_locations']:
        top_locs_df = pd.DataFrame(location_analysis['top_locations'][:10])
        top_locs_df.index = range(1, len(top_locs_df) + 1)
        st.dataframe(top_locs_df, use_container_width=True)


def render_communication_patterns(df, analyzer):
    """Render communication patterns"""
    st.markdown("## 📞 Communication Patterns")
    
    comm_patterns = analyzer.get_communication_patterns()
    
    # Duration statistics
    if 'duration_stats' in comm_patterns:
        st.markdown("### ⏱️ Call Duration Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        stats = comm_patterns['duration_stats']
        with col1:
            st.metric("Total Duration", f"{stats['total_duration_hours']:.1f} hrs")
        with col2:
            st.metric("Average Duration", f"{stats['avg_duration']:.0f} sec")
        with col3:
            st.metric("Short Calls (<30s)", f"{stats['short_calls_under_30s']:,}")
        with col4:
            st.metric("Long Calls (>5min)", f"{stats['long_calls_over_5min']:,}")
        
        st.markdown("---")
        
        # ===== VIOLIN PLOTS - CALL DURATION DISTRIBUTION =====
        st.markdown("### 🎻 Call Duration Distribution")
        st.caption("Beautiful visualization of duration patterns")
        
        calls_df = df[df['Call_Category'].isin(['Incoming Call', 'Outgoing Call'])].copy()
        
        if len(calls_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Violin plot for incoming vs outgoing
                fig = go.Figure()
                
                incoming_durations = calls_df[calls_df['Call_Category'] == 'Incoming Call']['Dur(s)']
                outgoing_durations = calls_df[calls_df['Call_Category'] == 'Outgoing Call']['Dur(s)']
                
                fig.add_trace(go.Violin(
                    y=incoming_durations,
                    name='Incoming',
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor='rgba(102, 126, 234, 0.5)',
                    line_color='#667eea',
                    opacity=0.8
                ))
                
                fig.add_trace(go.Violin(
                    y=outgoing_durations,
                    name='Outgoing',
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor='rgba(245, 87, 108, 0.5)',
                    line_color='#f5576c',
                    opacity=0.8
                ))
                
                fig.update_layout(
                    title="Call Duration Distribution (Incoming vs Outgoing)",
                    yaxis_title="Duration (seconds)",
                    template="plotly_dark",
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Treemap for contact frequency
                st.markdown("### 🗂️ Contact Frequency Treemap")
                st.caption("Hierarchical view of top contacts")
                
                contact_counts = calls_df['B_Party_Clean'].value_counts().head(20)
                
                treemap_data = pd.DataFrame({
                    'Contact': contact_counts.index,
                    'Count': contact_counts.values
                })
                
                # Add categories based on frequency
                treemap_data['Category'] = treemap_data['Count'].apply(
                    lambda x: 'Very Frequent (20+)' if x >= 20 
                    else 'Frequent (10-19)' if x >= 10 
                    else 'Moderate (5-9)' if x >= 5 
                    else 'Occasional (1-4)'
                )
                
                fig = px.treemap(
                    treemap_data,
                    path=['Category', 'Contact'],
                    values='Count',
                    color='Count',
                    color_continuous_scale='Purples',
                    title="Top 20 Contacts by Frequency"
                )
                
                fig.update_layout(
                    template="plotly_dark",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Daily patterns
    st.markdown("---")
    st.markdown("### 📅 Daily Activity Patterns")
    
    daily = comm_patterns['daily_patterns']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Average Daily Activity", f"{daily['avg_daily_activity']:.0f}")
        st.metric("Max Daily Activity", f"{daily['max_daily_activity']:,}")
    
    with col2:
        st.metric("Min Daily Activity", f"{daily['min_daily_activity']:,}")
        st.metric("Active Days", f"{daily['active_days']:,}")
    
    # Day of week distribution
    st.markdown("### 📆 Day of Week Distribution")
    
    dow_data = pd.DataFrame(list(comm_patterns['day_of_week'].items()),
                           columns=['Day', 'Count'])
    
    # Order days properly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_data['Day'] = pd.Categorical(dow_data['Day'], categories=day_order, ordered=True)
    dow_data = dow_data.sort_values('Day')
    
    fig = go.Figure(data=[
        go.Bar(x=dow_data['Day'], y=dow_data['Count'],
              marker_color='#764ba2',
              text=dow_data['Count'],
              textposition='outside')
    ])
    
    fig.update_layout(
        title="Activity by Day of Week",
        xaxis_title="Day",
        yaxis_title="Count",
        template="plotly_dark",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_search_filter(df):
    """Render search and filter interface"""
    st.markdown("## 🔍 Advanced Search & Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_number = st.text_input("Search by Number", "")
    
    with col2:
        call_type_filter = st.multiselect("Call Type", df['Call_Category'].unique())
    
    with col3:
        time_period_filter = st.multiselect("Time Period", df['TimePeriod'].unique())
    
    # Date range filter
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", df['DateTime'].min())
    
    with col2:
        end_date = st.date_input("End Date", df['DateTime'].max())
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_number:
        filtered_df = filtered_df[filtered_df['B_Party_Clean'].str.contains(search_number, na=False)]
    
    if call_type_filter:
        filtered_df = filtered_df[filtered_df['Call_Category'].isin(call_type_filter)]
    
    if time_period_filter:
        filtered_df = filtered_df[filtered_df['TimePeriod'].isin(time_period_filter)]
    
    filtered_df = filtered_df[
        (filtered_df['DateTime'].dt.date >= start_date) &
        (filtered_df['DateTime'].dt.date <= end_date)
    ]
    
    st.markdown(f"### 📊 Results: {len(filtered_df)} records")
    
    if len(filtered_df) > 0:
        # Define display columns - only include those that exist
        all_display_cols = [
            'DateTime', 'Call Type', 'B_Party_Clean', 'Dur(s)', 
            'First CGI', 'First CGI Lat/Long', 'IMEI', 'IMSI'
        ]
        # Filter to only existing columns
        display_cols = [col for col in all_display_cols if col in filtered_df.columns]
        
        st.dataframe(filtered_df[display_cols], use_container_width=True, height=500)
    
    # Export button
    if st.button("📥 Export Filtered Results to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"filtered_cdr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def render_reports(df, analyzer):
    """Render report generation"""
    st.markdown("## 📄 Investigation Reports")
    
    st.info("Report generation feature - Select report type and parameters")
    
    report_type = st.selectbox(
        "Report Type",
        ["Summary Report", "Temporal Analysis Report", "Contact Network Report", 
         "Location Intelligence Report", "Comprehensive Investigation Report"]
    )
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            st.markdown("### 📋 Investigation Summary Report")
            
            # Basic info
            st.markdown(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Total Records Analyzed:** {len(df):,}")
            st.markdown(f"**Date Range:** {df['DateTime'].min()} to {df['DateTime'].max()}")
            
            # Key findings
            st.markdown("### 🔍 Key Findings")
            
            temporal = analyzer.get_temporal_analysis()
            contact = analyzer.get_contact_analysis()
            
            findings = []
            
            # Night activity
            night_pct = temporal['night_day_summary']['night_percentage']
            if night_pct > 30:
                findings.append(f"⚠️ **High night activity:** {night_pct:.1f}% of communications occur during night hours (22:00-06:00)")
            
            # Top contacts
            top_contact = list(contact['top_contacts'].items())[0]
            findings.append(f"📞 **Most frequent contact:** {top_contact[0]} ({top_contact[1]} interactions)")
            
            # Burst activity
            comm = analyzer.get_communication_patterns()
            if comm.get('burst_activity'):
                findings.append(f"🔥 **Burst activity detected:** {len(comm['burst_activity'])} periods of unusually high activity")
            
            for finding in findings:
                st.markdown(finding)
            
            st.success("✅ Report generated successfully!")


if __name__ == "__main__":
    main()
