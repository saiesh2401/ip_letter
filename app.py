import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import shutil
import datetime
import json
import gc
from backend import ISPProcessor, BankLetterProcessor

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

# --- PAGINATION HELPER ---
def render_pagination(df, page_key, page_size=10000, render_controls=True):
    """
    Render pagination controls and return the current page slice of the dataframe.
    
    Args:
        df: Full dataframe to paginate
        page_key: Unique key for this pagination instance (e.g., 'airtel_page', 'jio_page')
        page_size: Number of rows per page (default 10000)
        render_controls: Whether to render the UI controls (default True)
    
    Returns:
        Tuple of (paginated_df, start_row, end_row, total_rows, current_page, total_pages)
    """
    # Initialize page state
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    
    total_rows = len(df)
    total_pages = max(1, (total_rows - 1) // page_size + 1)
    
    # Ensure current page is valid
    if st.session_state[page_key] >= total_pages:
        st.session_state[page_key] = total_pages - 1
    if st.session_state[page_key] < 0:
        st.session_state[page_key] = 0
    
    current_page = st.session_state[page_key]
    start_idx = current_page * page_size
    end_idx = min(start_idx + page_size, total_rows)
    
    # Get current page slice
    page_df = df.iloc[start_idx:end_idx]
    
    # Only render controls if requested
    if render_controls:
        # Render pagination controls
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ First", key=f"{page_key}_first", disabled=(current_page == 0)):
                st.session_state[page_key] = 0
                st.rerun()
        
        with col2:
            if st.button("⬅️ Prev", key=f"{page_key}_prev", disabled=(current_page == 0)):
                st.session_state[page_key] -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"**Page {current_page + 1} of {total_pages}**")
            st.caption(f"Showing rows {start_idx + 1:,} - {end_idx:,} of {total_rows:,}")
        
        with col4:
            if st.button("Next ➡️", key=f"{page_key}_next", disabled=(current_page >= total_pages - 1)):
                st.session_state[page_key] += 1
                st.rerun()
        
        with col5:
            if st.button("Last ⏭️", key=f"{page_key}_last", disabled=(current_page >= total_pages - 1)):
                st.session_state[page_key] = total_pages - 1
                st.rerun()
        
        # Jump to page
        if total_pages > 1:
            jump_page = st.number_input(
                "Jump to page:",
                min_value=1,
                max_value=total_pages,
                value=current_page + 1,
                step=1,
                key=f"{page_key}_jump"
            )
            if jump_page - 1 != current_page:
                st.session_state[page_key] = jump_page - 1
                st.rerun()
    
    return page_df, start_idx + 1, end_idx, total_rows, current_page + 1, total_pages

# ----------------------

st.title("🚔 IFSO ISP Letter Generator")

# Logout Button
with st.sidebar:
    st.write(f"Logged in as: **vikram@delhi.com**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.write("---")
    st.subheader("🧹 Memory Management")
    st.caption("Clear memory if app becomes slow after processing large files")
    
    if st.button("🗑️ Clear Memory", type="secondary"):
        # Clear large data from session state
        keys_to_clear = []
        for key in st.session_state.keys():
            if key not in ['authenticated', 'processor', 'bank_processor']:
                keys_to_clear.append(key)
        
        for key in keys_to_clear:
            del st.session_state[key]
        
        # Force garbage collection
        gc.collect()
        
        st.success("✅ Memory cleared! App should be faster now.")
        st.rerun()

st.markdown("Automated tool for IFSO Special Cell.")

# Tabs for Main Functionalities
gen_tab, reply_tab, bank_tab = st.tabs(["🚀 Generator", "🔍 Reply Analyzer", "🏦 Bank Letters"])

# ==========================================
# TAB 1: GENERATOR (HTML -> Letters)
# ==========================================
with gen_tab:
    st.header("Generate Request Letters")
    st.write("Upload the **Google Subscriber Info HTML** file to generate legal requests for Jio, Airtel, and VI.")
    
    # Initialize Session State
    # Check if processor exists and is up-to-date (has new methods)
    if 'processor' not in st.session_state or not hasattr(st.session_state.processor, 'process_airtel_reply'):
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
            
            # Download All as ZIP button
            st.write("**Download Options:**")
            col_zip, col_spacer = st.columns([1, 3])
            
            with col_zip:
                # Create ZIP file with all generated files
                import zipfile
                import io
                from datetime import datetime
                
                zip_buffer = io.BytesIO()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                suspect_name = res.get("suspect_name", "Unknown")
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in res["generated_files"]:
                        if os.path.exists(file_path):
                            file_name = os.path.basename(file_path)
                            # Organize by ISP
                            if "JIO" in file_name:
                                zip_path = f"JIO/{file_name}"
                            elif "AIRTEL" in file_name:
                                zip_path = f"AIRTEL/{file_name}"
                            elif "VI" in file_name:
                                zip_path = f"VI/{file_name}"
                            else:
                                zip_path = file_name
                            zip_file.write(file_path, zip_path)
                
                zip_buffer.seek(0)
                
                st.download_button(
                    label="📦 Download All as ZIP",
                    data=zip_buffer,
                    file_name=f"{suspect_name}_ISP_Letters_{timestamp}.zip",
                    mime="application/zip",
                    key="download_all_isp_letters",
                    type="primary"
                )
            
            st.write("---")
            
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

# ==========================================
# TAB 2: REPLY ANALYZER (Airtel Zip -> Analysis)
# ==========================================
with reply_tab:
    st.header("🔍 Reply Parsing Tool")
    st.info("Use this tool to extract raw IP data from ISP Reply files (Zip/7z).")
    
    col_airtel, col_jio, col_vi = st.columns(3)
    
    # -----------------------------------------------------------
    # AIRTEL LOGIC (LEFT COLUMN)
    # -----------------------------------------------------------
    with col_airtel:
        st.subheader("🔴 Airtel Reply Analysis")
        st.write("Upload the **zipped reply** from Airtel.")
        
        reply_file = st.file_uploader("Upload Airtel Zip", type=['zip'], key="reply_up_airtel")
        reply_pass = st.text_input("Zip Password", value="18Imc", type="password", key="reply_pass_airtel")
        
        
        col_analyze, col_reset = st.columns([1, 1])
        
        with col_analyze:
            analyze_btn = st.button("🔍 Analyze Airtel", key="analyze_airtel_btn", type="primary")
        
        with col_reset:
            if st.button("🔄 Reset", key="reset_airtel_btn"):
                # Clear Airtel-specific session state
                if 'airtel_results' in st.session_state:
                    del st.session_state['airtel_results']
                if 'airtel_page' in st.session_state:
                    del st.session_state['airtel_page']
                gc.collect()
                st.success("✅ Airtel analysis reset!")
                st.rerun()
        
        if reply_file and analyze_btn:
            reply_path = "temp_airtel.zip"
            with open(reply_path, "wb") as f:
                f.write(reply_file.getbuffer())
                
            with st.spinner("Decrypting and Analyzing Airtel Data..."):
                processor = st.session_state.processor
                results_dict, msg = processor.process_airtel_reply(reply_path, reply_pass)
                
                if results_dict is None:
                    st.error(msg)
                else:
                    st.success("Analysis Complete!")
                    
                    hits_df = results_dict['hits_df']
                    misses = results_dict['misses']
                    
                    c1, c2 = st.columns(2)
                    c1.metric(label="Valid Hits", value=len(hits_df))
                    c2.metric(label="Empty/Skipped Files", value=len(misses))
                    
                    # Show Hits
                    if not hits_df.empty:
                        st.subheader("✅ Valid Data Found")
                        
                        # Show summary statistics
                        total_rows = len(hits_df)
                        st.info(f"📊 **Total Records Found:** {total_rows:,} rows")
                        
                        # Prepare display dataframe
                        display_df = hits_df.drop(columns=["CSV_Path"], errors="ignore")
                        
                        # Use pagination for large datasets
                        if total_rows > 10000:
                            st.write("---")
                            st.subheader("📄 Paginated Data View")
                            
                            # Render pagination controls and get current page
                            page_df, start_row, end_row, total, current_page, total_pages = render_pagination(
                                display_df, 
                                'airtel_page', 
                                page_size=10000
                            )
                            
                            # Display current page
                            st.dataframe(page_df, width='stretch', height=500)
                        else:
                            # For small datasets, show all data
                            st.dataframe(display_df, width='stretch', height=500)
                        
                        # Evidence Downloads
                        st.subheader("📂 Raw Evidence Files")
                        if 'CSV_Path' in hits_df.columns:
                            unique_files = hits_df[['Source_File', 'CSV_Path']].drop_duplicates()
                            for idx, row in unique_files.iterrows():
                                fname = row['Source_File']
                                fpath = row['CSV_Path']
                                if fpath and os.path.exists(fpath):
                                    bname = os.path.basename(fpath)
                                    
                                    # Download Button
                                    with open(fpath, "rb") as f:
                                        st.download_button(
                                            label=f"📥 Download {bname}",
                                            data=f,
                                            file_name=bname,
                                            mime="text/csv",
                                            key=f"ev_airtel_{idx}"
                                        )
                                    
                                    # Preview Content (Airtel Specific)
                                    with st.expander(f"👁️ View Content: {bname}"):
                                        try:
                                            # Read lines to find header
                                            with open(fpath, "r", encoding="latin1") as f2:
                                                lines = f2.readlines()
                                            
                                            header_idx = -1
                                            for i, line in enumerate(lines):
                                                if "DSL_User_ID" in line:
                                                    header_idx = i
                                                    break
                                            
                                            if header_idx != -1:
                                                try:
                                                    sub_df = pd.read_csv(fpath, skiprows=header_idx, header=0, encoding='latin1', quotechar="'", skipinitialspace=True, on_bad_lines='skip', engine='python')
                                                except:
                                                    sub_df = pd.read_csv(fpath, skiprows=header_idx, header=0, encoding='latin1', quotechar="'", skipinitialspace=True, engine='python')
                                                
                                                # Filter footer
                                                if 'DSL_User_ID' in sub_df.columns:
                                                    sub_df = sub_df[~sub_df['DSL_User_ID'].astype(str).str.contains("System generated", case=False, na=False)]
                                                st.dataframe(sub_df, width='stretch')
                                            else:
                                                st.warning("No standard Airtel header found.")
                                                st.text("".join(lines[:20]))
                                        except Exception as e:
                                            st.error(f"Error parsing: {e}")

                        # Combined Excel
                        import io
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                             hits_df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Combined Airtel Excel",
                            data=buffer.getvalue(),
                            file_name="Airtel_Hits_Combined.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="dl_airtel_comb"
                        )
                        
                        # Clean up large dataframe from memory
                        del hits_df, display_df, buffer
                        gc.collect()
                        
                    else:
                        st.warning("No valid data rows found in this file.")
                        
                    if misses:
                        with st.expander("See Empty/No-Record Files"):
                            st.write(misses)

    # -----------------------------------------------------------
    # JIO LOGIC (RIGHT COLUMN)
    # -----------------------------------------------------------
    with col_jio:
        st.subheader("🔵 Jio Reply Analysis")
        st.write("Upload the **.7z or .zip reply** from Jio.")
        
        jio_file = st.file_uploader("Upload Jio .7z or .zip", type=['7z', 'zip'], key="reply_up_jio")
        
        
        col_analyze, col_reset = st.columns([1, 1])
        
        with col_analyze:
            analyze_btn = st.button("🔍 Analyze Jio", key="analyze_jio_btn", type="primary")
        
        with col_reset:
            if st.button("🔄 Reset", key="reset_jio_btn"):
                # Clear Jio-specific session state
                if 'jio_results' in st.session_state:
                    del st.session_state['jio_results']
                if 'jio_page' in st.session_state:
                    del st.session_state['jio_page']
                gc.collect()
                st.success("✅ Jio analysis reset!")
                st.rerun()
        
        if jio_file and analyze_btn:
            # Preserve the original file extension (.7z or .zip)
            file_ext = os.path.splitext(jio_file.name)[1]
            jio_path = f"temp_jio{file_ext}"
            with open(jio_path, "wb") as f:
                f.write(jio_file.getbuffer())
                
            with st.spinner("Extracting and Analyzing Jio Data..."):
                processor = st.session_state.processor
                results_dict, msg = processor.process_jio_reply(jio_path)
                
                if results_dict is None:
                    st.error(msg)
                else:
                    st.success("Analysis Complete!")
                    
                    hits_df = results_dict['hits_df']
                    misses = results_dict['misses']
                    
                    c1, c2 = st.columns(2)
                    c1.metric(label="Valid Hits", value=len(hits_df))
                    c2.metric(label="Empty/Skipped Files", value=len(misses))
                    
                    if not hits_df.empty:
                        st.subheader("✅ Valid Data Found")
                        
                        # Show summary statistics
                        total_rows = len(hits_df)
                        st.info(f"📊 **Total Records Found:** {total_rows:,} rows")
                        
                        # Prepare display dataframe
                        display_df = hits_df.drop(columns=["CSV_Path"], errors="ignore")
                        
                        # Use pagination for large datasets
                        if total_rows > 10000:
                            st.write("---")
                            st.subheader("📄 Paginated Data View")
                            
                            # Render pagination controls and get current page
                            page_df, start_row, end_row, total, current_page, total_pages = render_pagination(
                                display_df, 
                                'jio_page', 
                                page_size=10000
                            )
                            
                            # Display current page
                            st.dataframe(page_df, width='stretch', height=500)
                        else:
                            # For small datasets, show all data
                            st.dataframe(display_df, width='stretch', height=500)
                        
                        st.subheader("📂 Raw Evidence Files")
                        if 'CSV_Path' in hits_df.columns:
                            unique_files = hits_df[['Source_File', 'CSV_Path']].drop_duplicates()
                            for idx, row in unique_files.iterrows():
                                fname = row['Source_File']
                                fpath = row['CSV_Path']
                                if fpath and os.path.exists(fpath):
                                    bname = os.path.basename(fpath)
                                    
                                    # Download
                                    with open(fpath, "rb") as f:
                                        st.download_button(
                                            label=f"📥 Download {bname}",
                                            data=f,
                                            file_name=bname,
                                            mime="text/csv", 
                                            key=f"ev_jio_{idx}"
                                        )
                                    
                                    # Preview (Standard CSV)
                                    with st.expander(f"👁️ View Content: {bname}"):
                                        try:
                                            # Jio is simpler, just read csv
                                            # Read all columns as strings to prevent Arrow serialization errors
                                            sub_df = pd.read_csv(fpath, on_bad_lines='skip', encoding='latin1', low_memory=False, dtype=str)
                                            st.dataframe(sub_df, width='stretch')
                                        except Exception as e:
                                            st.error(f"Error previewing: {e}")

                        # Combined Excel
                        import io
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                             hits_df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Combined Jio Excel",
                            data=buffer.getvalue(),
                            file_name="Jio_Hits_Combined.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="dl_jio_comb"
                        )
                        
                        # Clean up large dataframe from memory
                        del hits_df, display_df, buffer
                        gc.collect()
                        
                    else:
                         st.warning("No valid data rows found.")
                         
                    if misses:
                        with st.expander("See Missed Files"):
                            st.write(misses)

    # -----------------------------------------------------------
    # VI LOGIC (RIGHT COLUMN)
    # -----------------------------------------------------------
    with col_vi:
        st.subheader("🟢 VI Reply Analysis")
        st.write("Upload the **zipped reply** from VI.")
        
        vi_file = st.file_uploader("Upload VI Zip", type=['zip'], key="reply_up_vi")
        
        
        col_analyze, col_reset = st.columns([1, 1])
        
        with col_analyze:
            analyze_btn = st.button("🔍 Analyze VI", key="analyze_vi_btn", type="primary")
        
        with col_reset:
            if st.button("🔄 Reset", key="reset_vi_btn"):
                # Clear VI-specific session state
                if 'vi_results' in st.session_state:
                    del st.session_state['vi_results']
                if 'vi_page' in st.session_state:
                    del st.session_state['vi_page']
                gc.collect()
                st.success("✅ VI analysis reset!")
                st.rerun()
        
        if vi_file and analyze_btn:
            vi_path = "temp_vi.zip"
            with open(vi_path, "wb") as f:
                f.write(vi_file.getbuffer())
                
            with st.spinner("Extracting and Analyzing VI Data..."):
                processor = st.session_state.processor
                results_dict, msg = processor.process_vi_reply(vi_path)
                
                if results_dict is None:
                    st.error(msg)
                else:
                    st.success("Analysis Complete!")
                    
                    total_rows = results_dict['total_rows']
                    output_file = results_dict['output_file']
                    sample_data = results_dict['sample_data']
                    misses = results_dict['misses']
                    
                    c1, c2 = st.columns(2)
                    c1.metric(label="📊 Total Records", value=f"{total_rows:,}")
                    c2.metric(label="⚠️ Skipped Files", value=len(misses))
                    
                    if total_rows > 0:
                        st.subheader("✅ Data Processing Complete")
                        
                        # Show summary info
                        st.info(f"""
                        **Processing Summary:**
                        - Total records found: **{total_rows:,}** rows
                        - Output file size: **{os.path.getsize(output_file) / (1024*1024):.1f} MB** (Excel format)
                        - Files processed successfully
                        """)
                        
                        # Show sample preview
                        if sample_data is not None and not sample_data.empty:
                            st.subheader("📋 Sample Preview (First 100 Rows)")
                            display_sample = sample_data.drop(columns=["CSV_Path"], errors="ignore")
                            st.dataframe(display_sample, width='stretch', height=400)
                        
                        # Download button for full Excel file
                        st.subheader("📥 Download Complete Results")
                        with open(output_file, "rb") as f:
                            st.download_button(
                                label=f"📥 Download Full Excel ({total_rows:,} rows)",
                                data=f,
                                file_name="VI_Analysis_Complete.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="dl_vi_full"
                            )
                        
                        st.caption("💡 The full dataset has been saved as an Excel file for download. Excel format is 5-10x smaller than CSV!")
                        
                    else:
                         st.warning("No valid data rows found.")
                         
                    if misses:
                        with st.expander("See Skipped Files"):
                            st.write(misses)


# ==========================================
# TAB 3: BANK LETTERS (Excel -> Bank Letters)
# ==========================================
with bank_tab:
    st.header("🏦 Bank Transaction Letter Generator")
    st.info("Upload the transaction Excel file to generate bank-specific letters for different transaction types.")
    
    # Display backend version for debugging
    if hasattr(BankLetterProcessor, 'VERSION'):
        st.caption(f"Backend Version: {BankLetterProcessor.VERSION}")
    else:
        st.warning("⚠️ Running OLD backend version - please refresh or contact admin")
    
    # Initialize Bank Letter Processor
    if 'bank_processor' not in st.session_state:
        st.session_state.bank_processor = BankLetterProcessor(output_dir="Generated_Letters")
    
    # File Upload
    bank_excel_file = st.file_uploader("Upload Transaction Excel File (sample.xlsx)", type=['xlsx'], key="bank_excel_upload")
    
    if bank_excel_file is not None:
        # Save uploaded file
        temp_excel_path = "temp_bank_transactions.xlsx"
        with open(temp_excel_path, "wb") as f:
            f.write(bank_excel_file.getbuffer())
        
        st.success(f"Loaded: {bank_excel_file.name}")
        
        # Parse Excel
        processor = st.session_state.bank_processor
        sheets, error = processor.parse_bank_excel(temp_excel_path)
        
        if error:
            st.error(error)
        else:
            st.session_state.bank_sheets = sheets
            
            # Display sheet information
            st.subheader("📊 Transaction Summary")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Money Transfers", len(sheets['Money Transfer to']))
            with col2:
                st.metric("On Hold", len(sheets['Transaction put on hold']))
            with col3:
                st.metric("ATM Withdrawals", len(sheets['Withdrawal through ATM']))
            with col4:
                st.metric("Cheque Withdrawals", len(sheets['Cash Withdrawal through Cheque']))
            with col5:
                st.metric("AEPS", len(sheets['AEPS']))
            
            # Layer Detection for Sheet 1
            max_layers = processor.get_available_layers(sheets['Money Transfer to'])
            
            
            st.write("---")
            st.subheader("📝 Letter Customization")
            
            # Custom Subject Line
            st.write("**Subject Line:**")
            default_subject = "Notice to Freeze & provide details of bank accounts in the case FIR no. 201/25, U/s 318(4)/319(2)/61(2)/3(5), Dated 08/07/25, PS Special Cell (L2)"
            custom_subject = st.text_area(
                "Enter custom subject line for the bank letters",
                value=default_subject,
                height=80,
                key="custom_subject",
                help="This will appear as the subject line in all generated bank letters"
            )
            
            # Custom Case Description
            st.write("**Case Description:**")
            default_message = """It is submitted that a complaint from Sh. Akhilesh Dutt has been received at IFSO/Special Cell office regarding cheating on pretext of investment through WhatsApp group "TATA CAPITAL MONEYFY". It was alleged that they were added in what's app group. The complainants were induced to invest in multiple companies through their respective bank accounts amounting to Rs.77,30,040/- 
               During the course of investigation, it revealed that the complainant transferred the amount in below mentioned accounts."""
            
            custom_message = st.text_area(
                "Enter case description/details for the bank letters",
                value=default_message,
                height=150,
                key="custom_message",
                help="This will appear in the body of all generated bank letters"
            )
            
            
            # Custom Release Order Details (for money release letters)
            st.write("**Release Order Details (for Money Release Letters):**")
            
            # Court Order - will be justified/centered in letter
            st.write("*Court Order (will be justified in letter):*")
            default_court_order = "The Hon'ble Court of Sh. Yashdeep Chahal, Judicial Magisrate-01, Patiala House Courts, New Delhi has directed to the concerned bank manager to release the amount, whichever is available/lying in the beneficiary bank account in favor of the complainant to the below mentioned account. (order attached herewith)"
            
            custom_court_order = st.text_area(
                "Enter court order details",
                value=default_court_order,
                height=100,
                key="custom_court_order",
                help="This will be justified/centered in the letter"
            )
            
            # Beneficiary Account - will be left-aligned in letter
            st.write("*Beneficiary Account Details (will be left-aligned in letter):*")
            default_beneficiary = """Sh. Akhilesh Dutt
Bank Account No. 629301106296  (ICICI Bank)
(IFSC Code : ICIC0006293) 
Branch : Rajouri Garden, New Delhi"""
            
            custom_beneficiary = st.text_area(
                "Enter beneficiary account details",
                value=default_beneficiary,
                height=100,
                key="custom_beneficiary",
                help="This will be left-aligned in the letter"
            )
            
            # Store in session state for use in letter generation
            st.session_state.letter_subject = custom_subject
            st.session_state.letter_message = custom_message
            st.session_state.letter_court_order = custom_court_order
            st.session_state.letter_beneficiary = custom_beneficiary
            
            st.write("---")
            st.subheader("⚙️ Configuration")
            
            # Sheet Selection
            st.write("**Select Transaction Types to Process:**")
            col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
            
            with col_s1:
                process_sheet1 = st.checkbox("Money Transfer", value=True, key="proc_s1")
            with col_s2:
                process_sheet2 = st.checkbox("On Hold", value=True, key="proc_s2")
            with col_s3:
                process_sheet3 = st.checkbox("ATM", value=True, key="proc_s3")
            with col_s4:
                process_sheet4 = st.checkbox("Cheque", value=True, key="proc_s4")
            with col_s5:
                process_sheet5 = st.checkbox("AEPS", value=True, key="proc_s5")
            
            # Layer Selection for Sheet 1
            if process_sheet1:
                st.write("---")
                st.write("**Money Transfer Layer Selection:**")
                
                if max_layers > 0:
                    st.info(f"📌 Transactions exist for **{max_layers} layer(s)**. Select how many layers to include in the letters.")
                    
                    num_layers = st.number_input(
                        f"Select number of layers (1 to {max_layers})",
                        min_value=1,
                        max_value=max_layers,
                        value=min(2, max_layers),
                        step=1,
                        key="layer_select"
                    )
                else:
                    st.warning("No layer information found in Money Transfer sheet.")
                    num_layers = 1
            
            # Generate Button
            st.write("---")
            if st.button("🚀 Generate Bank Letters", type="primary"):
                all_generated_files = []
                
                with st.spinner("Generating bank letters..."):
                    progress_bar = st.progress(0)
                    total_tasks = sum([process_sheet1, process_sheet2, process_sheet3, process_sheet4, process_sheet5])
                    current_task = 0
                    
                    try:
                        # Sheet 1: Money Transfer
                        if process_sheet1:
                            st.write("📝 Processing Money Transfer transactions...")
                            files = processor.generate_layerwise_letters(
                                sheets['Money Transfer to'], 
                                num_layers,
                                custom_subject=st.session_state.get('letter_subject'),
                                custom_message=st.session_state.get('letter_message')
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 2: On Hold
                        if process_sheet2:
                            st.write("📝 Processing Transaction On Hold...")
                            files = processor.generate_money_release_letters(
                                sheets['Transaction put on hold'],
                                custom_subject=st.session_state.get('letter_subject'),
                                custom_message=st.session_state.get('letter_message'),
                                custom_court_order=st.session_state.get('letter_court_order'),
                                custom_beneficiary=st.session_state.get('letter_beneficiary')
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 3: ATM
                        if process_sheet3:
                            st.write("📝 Processing ATM Withdrawals...")
                            files = processor.generate_atm_letters(
                                sheets['Withdrawal through ATM'],
                                custom_subject=st.session_state.get('letter_subject'),
                                custom_message=st.session_state.get('letter_message')
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 4: Cheque
                        if process_sheet4:
                            st.write("📝 Processing Cheque Withdrawals...")
                            files = processor.generate_cheque_letters(
                                sheets['Cash Withdrawal through Cheque'],
                                custom_subject=st.session_state.get('letter_subject'),
                                custom_message=st.session_state.get('letter_message')
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 5: AEPS
                        if process_sheet5:
                            st.write("📝 Processing AEPS Withdrawals...")
                            files = processor.generate_aeps_letters(
                                sheets['AEPS'],
                                custom_subject=st.session_state.get('letter_subject'),
                                custom_message=st.session_state.get('letter_message')
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Store results
                        st.session_state.bank_generated_files = all_generated_files
                        
                        st.balloons()
                        st.success(f"✅ Successfully generated {len(all_generated_files)} bank letters!")
                        
                    except Exception as e:
                        st.error(f"Error generating letters: {e}")
                        st.exception(e)
            
            # Display Results
            if 'bank_generated_files' in st.session_state and st.session_state.bank_generated_files:
                st.write("---")
                st.subheader("📥 Generated Letters")
                
                # Group by transaction type
                files_by_type = {}
                for file_info in st.session_state.bank_generated_files:
                    txn_type = file_info['type']
                    if txn_type not in files_by_type:
                        files_by_type[txn_type] = []
                    files_by_type[txn_type].append(file_info)
                
                # Download All as ZIP button
                st.write("**Download Options:**")
                col_zip, col_spacer = st.columns([1, 3])
                
                with col_zip:
                    # Create ZIP file with all generated letters
                    import zipfile
                    import io
                    from datetime import datetime
                    
                    zip_buffer = io.BytesIO()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for file_info in st.session_state.bank_generated_files:
                            if os.path.exists(file_info['path']):
                                # Add file to ZIP with organized folder structure
                                file_name = os.path.basename(file_info['path'])
                                txn_type = file_info['type']
                                # Create a clean folder name
                                folder_name = txn_type.replace(" ", "_")
                                zip_path = f"{folder_name}/{file_name}"
                                zip_file.write(file_info['path'], zip_path)
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="📦 Download All as ZIP",
                        data=zip_buffer,
                        file_name=f"Bank_Letters_{timestamp}.zip",
                        mime="application/zip",
                        key="download_all_bank_letters",
                        type="primary"
                    )
                
                st.write("---")
                
                # Display in tabs by transaction type
                if len(files_by_type) > 0:
                    type_tabs = st.tabs(list(files_by_type.keys()))
                    
                    for idx, (txn_type, tab) in enumerate(zip(files_by_type.keys(), type_tabs)):
                        with tab:
                            st.write(f"**{txn_type} Letters**")
                            
                            # Display each bank's letter
                            for file_info in files_by_type[txn_type]:
                                col_info, col_download = st.columns([3, 1])
                                
                                with col_info:
                                    st.write(f"🏦 **{file_info['bank']}**")
                                    st.caption(f"Transactions: {file_info['count']}")
                                
                                with col_download:
                                    if os.path.exists(file_info['path']):
                                        with open(file_info['path'], "rb") as f:
                                            file_name = os.path.basename(file_info['path'])
                                            
                                            if file_name.endswith('.pdf'):
                                                mime_type = "application/pdf"
                                            else:
                                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                                
                                            st.download_button(
                                                label="📥 Download",
                                                data=f,
                                                file_name=file_name,
                                                mime=mime_type,
                                                key=f"dl_bank_{idx}_{file_name}"
                                            )
                                
                                st.write("---")
                
                # ---- Layerwise Flow Diagram ----
                if process_sheet1 and 'Money Transfer to' in sheets and not sheets['Money Transfer to'].empty:
                    st.write("---")
                    st.subheader("📊 Layerwise Transaction Flow")
                    st.caption("Interactive visualization of money tracking across layers")
                    
                    try:
                        import json
                        import streamlit.components.v1 as components
                        import pandas as pd # Added import for pandas
                        import os # Added import for os
                        
                        df_mt = sheets['Money Transfer to']
                        txns = []
                        df_clean = df_mt.dropna(subset=['Account No', 'Layer'])
                        
                        for idx, row in df_clean.iterrows():
                            acc = row.get('Account No', '')
                            if pd.isna(acc) or not str(acc).strip(): continue
                            acc_str = str(int(acc)) if isinstance(acc, (int, float)) else str(acc)
                            
                            bank = row.get('Bank/FIs', '')
                            if pd.isna(bank) or not str(bank).strip():
                                bank = str(row.get('Action Taken By bank', 'Unknown'))
                            else:
                                bank = str(bank)
                                
                            layer = row.get('Layer', 1)
                            try:
                                layer = int(layer)
                            except ValueError:
                                continue
                                
                            amt = row.get('Transaction Amount', getattr(row, 'Disputed Amount', 0))
                            if pd.isna(amt): amt = 0
                                
                            date = row.get('Transaction Date', '')
                            if pd.isna(date): date = ''
                            else: date = str(date)
                            
                            txns.append({
                                'id': int(idx),
                                'layer': layer,
                                'bank': bank,
                                'amount': float(amt) if amt else 0.0,
                                'account': acc_str,
                                'date': date,
                                'targetLayer': None
                            })
                            
                        # Add simplistic visual linking between available layers
                        for t in txns:
                            has_next_layer = any(x['layer'] == t['layer'] + 1 for x in txns)
                            if has_next_layer:
                                t['targetLayer'] = t['layer'] + 1
                                
                        diagram_path = "bank_diagram/embedded_diagram.html"
                        if os.path.exists(diagram_path):
                            with open(diagram_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                                
                            json_data = json.dumps(txns)
                            # Give the diagram engine a second to initialize before loading data
                            script_injection = f"<script>window.addEventListener('load', function() {{ setTimeout(() => window.loadTransactionData({json_data}), 500); }});</script>"
                            
                            if "</body>" in html_content:
                                html_content = html_content.replace("</body>", f"{script_injection}\n</body>")
                            else:
                                html_content += script_injection
                                
                            # Render the HTML block directly into Streamlit
                            components.html(html_content, height=850, scrolling=True)
                        else:
                            st.warning("Visualization template not found in deployment.")
                    except Exception as e:
                        st.error(f"Error rendering diagram: {e}")
