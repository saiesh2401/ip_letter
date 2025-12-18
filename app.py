import streamlit as st
import os
import shutil
import datetime
from backend import ISPProcessor

# Set page config
st.set_page_config(page_title="IFSO ISP Tool", page_icon="🚔", layout="wide")

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    st.title("Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "vikram@delhi.com" and password == "honeysingh@1":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

if not st.session_state.authenticated:
    check_login()
    st.stop()
# ----------------------

st.title("🚔 IFSO ISP Letter Generator")

# Logout Button
with st.sidebar:
    st.write(f"Logged in as: **vikram@delhi.com**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("Upload the **Google Subscriber Info HTML** file to generate legal requests for Jio, Airtel, and VI.")

# Initialize Session State
if 'processor' not in st.session_state:
    st.session_state.processor = ISPProcessor(output_dir="Generated_Letters", cache_file="isp_cache.json")
if 'results' not in st.session_state:
    st.session_state.results = None

# File Uploader
uploaded_file = st.file_uploader("Choose HTML File", type=['html'])

if uploaded_file is not None:
    # Save uploaded file temporarily because backend expects a path
    temp_path = os.path.join("temp_upload.html")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"Loaded: {uploaded_file.name}")
    
    # 1. Parse immediately to get defaults
    processor = st.session_state.processor
    try:
        extracted_meta, raw_data = processor.parse_html(temp_path)
        st.session_state.extracted_meta = extracted_meta
        st.session_state.raw_data = raw_data
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        st.session_state.extracted_meta = {}
        st.session_state.raw_data = []

    # 2. Input Fields
    st.subheader("📝 Case Details")
    col_a, col_b = st.columns(2)
    with col_a:
        input_name = st.text_input("Accused Name", value=st.session_state.extracted_meta.get("name", ""))
        input_fir = st.text_input("FIR No.", value="18/25")
    with col_b:
        input_email = st.text_input("Accused Email", value=st.session_state.extracted_meta.get("email", ""))
        input_date = st.text_input("FIR Date", value=datetime.datetime.now().strftime("%d.%m.%Y"))

    # Update metadata with user inputs
    final_metadata = {
        "name": input_name,
        "email": input_email,
        "fir_no": input_fir,
        "fir_date": input_date
    }

    if st.button("🚀 Generate Letters"):
        
        progress_bar = st.progress(0)
        logs = st.empty()

        try:
            suspect_name = input_name.replace(" ", "_")
            if not suspect_name: suspect_name = "Unknown"
            
            if not st.session_state.raw_data: # Use raw_data from session state
                st.error("No login records found in the file.")
            else:
                # Process Data
                status_text = st.empty()
                status_text.text("Identifying ISPs... This may take a moment...")
                
                def update_prog(current, total):
                    pct = int((current / total) * 100)
                    progress_bar.progress(pct)
                
                grouped_data = processor.process_data(st.session_state.raw_data, progress_callback=update_prog) # Use raw_data from session state
                status_text.text("Generating Documents...")
                
                # Save to Session State
                st.session_state.results = {
                    "grouped_data": grouped_data,
                    "metadata": final_metadata, # Use final_metadata
                    "suspect_name": suspect_name,
                    "generated_files": []
                }
                
                results = st.session_state.results
                
                # JIO
                if "JIO" in grouped_data:
                    s, m = processor.fill_jio_excel(grouped_data["JIO"], "JIO IP.xlsx", f"{suspect_name}_JIO_Data.xlsx")
                    if s: results["generated_files"].append(m)
                    
                    s, m = processor.fill_jio_txt(grouped_data["JIO"], f"{suspect_name}_JIO_Data.txt")
                    if s: results["generated_files"].append(m)
                    
                    s, m = processor.fill_word_letter(grouped_data["JIO"], "JIO", "JIO Template.docx", f"{suspect_name}_JIO_Request_Letter.docx", metadata=final_metadata)
                    if s: results["generated_files"].append(m)

                # AIRTEL
                if "AIRTEL" in grouped_data:
                    s, m = processor.fill_airtel_excel(grouped_data["AIRTEL"], "Airtel Format.xlsx", f"{suspect_name}_AIRTEL_Data.xlsx")
                    if s: results["generated_files"].append(m)
                    
                    s, m = processor.fill_word_letter(grouped_data["AIRTEL"], "AIRTEL", "Airtel Template.docx", f"{suspect_name}_AIRTEL_Request_Letter.docx", metadata=final_metadata)
                    if s: results["generated_files"].append(m)

                # VI
                if "VI" in grouped_data:
                    s, m = processor.fill_generic_excel(grouped_data["VI"], f"{suspect_name}_VI_Data.xlsx")
                    if s: results["generated_files"].append(m)
                    
                    s, m = processor.fill_word_letter(grouped_data["VI"], "VI", "VI Template.docx", f"{suspect_name}_VI_Request_Letter.docx", metadata=final_metadata)
                    if s: results["generated_files"].append(m)
                    
                st.session_state.results = results # Update with files
                st.balloons()
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)

    # --- Render Results if they exist ---
    if st.session_state.results:
        res = st.session_state.results
        metadata = res["metadata"]
        
        st.write("---")
        st.info(f"**Suspect:** {metadata.get('name')} | **Email:** {metadata.get('email')}")
        
        # UI Organization: Tabs
        tab_letters, tab_data = st.tabs(["📄 Request Letters (.docx)", "📊 IP Data Sheets (.xlsx)"])
        
        generated_files = res["generated_files"]
        
        # Helper to render a download button
        def render_btn(fpath, context_key):
             fname = os.path.basename(fpath)
             if not os.path.exists(fpath): return
             with open(fpath, "rb") as f:
                st.download_button(
                    label=f"Download {fname}",
                    data=f,
                    file_name=fname,
                    mime="application/octet-stream",
                    key=f"{context_key}_{fname}"
                )

        # Tab 1: Letters
        with tab_letters:
            st.subheader("Legal Request Letters")
            cols = st.columns(3)
            
            # Divide by ISP availability
            # JIO content
            if "JIO" in res["grouped_data"]:
                with cols[0]:
                    st.write("**Reliance Jio**")
                    st.caption(f"Found {len(res['grouped_data']['JIO'])} IPs")
                    for f in generated_files:
                        if "JIO" in f and f.endswith(".docx"):
                            render_btn(f, "tab1")
            
            # Airtel Content
            if "AIRTEL" in res["grouped_data"]:
                with cols[1]:
                    st.write("**Bharti Airtel**")
                    st.caption(f"Found {len(res['grouped_data']['AIRTEL'])} IPs")
                    for f in generated_files:
                        if "AIRTEL" in f and f.endswith(".docx"):
                            render_btn(f, "tab1")

            # VI Content
            if "VI" in res["grouped_data"]:
                with cols[2]:
                    st.write("**Vodafone Idea**")
                    st.caption(f"Found {len(res['grouped_data']['VI'])} IPs")
                    for f in generated_files:
                        if "VI" in f and f.endswith(".docx"):
                            render_btn(f, "tab1")

        # Tab 2: Excel Sheets
        with tab_data:
            st.subheader("Raw IP Data (Excel/Txt)")
            cols_d = st.columns(3)
            
            if "JIO" in res["grouped_data"]:
                with cols_d[0]:
                    st.write("**Reliance Jio**")
                    for f in generated_files:
                        if "JIO" in f and (f.endswith(".xlsx") or f.endswith(".txt")):
                            render_btn(f, "tab2")

            if "AIRTEL" in res["grouped_data"]:
                with cols_d[1]:
                    st.write("**Bharti Airtel**")
                    for f in generated_files:
                        if "AIRTEL" in f and f.endswith(".xlsx"):
                            render_btn(f, "tab2")

            if "VI" in res["grouped_data"]:
                with cols_d[2]:
                    st.write("**Vodafone Idea**")
                    for f in generated_files:
                        if "VI" in f and f.endswith(".xlsx"):
                            render_btn(f, "tab2")
