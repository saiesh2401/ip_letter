import streamlit as st
import pandas as pd
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
    
    col_airtel, col_jio = st.columns(2)
    
    # -----------------------------------------------------------
    # AIRTEL LOGIC (LEFT COLUMN)
    # -----------------------------------------------------------
    with col_airtel:
        st.subheader("🔴 Airtel Reply Analysis")
        st.write("Upload the **zipped reply** from Airtel.")
        
        reply_file = st.file_uploader("Upload Airtel Zip", type=['zip'], key="reply_up_airtel")
        reply_pass = st.text_input("Zip Password", value="18Imc", type="password", key="reply_pass_airtel")
        
        if reply_file and st.button("Analyze Airtel"):
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
                        display_df = hits_df.drop(columns=["CSV_Path"], errors="ignore")
                        st.dataframe(display_df, use_container_width=True, height=500)
                        
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
                                                st.dataframe(sub_df, use_container_width=True)
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
        st.write("Upload the **.7z reply** from Jio.")
        
        jio_file = st.file_uploader("Upload Jio .7z", type=['7z'], key="reply_up_jio")
        
        if jio_file and st.button("Analyze Jio"):
            jio_path = "temp_jio.7z"
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
                        display_df = hits_df.drop(columns=["CSV_Path"], errors="ignore")
                        st.dataframe(display_df, use_container_width=True, height=500)
                        
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
                                            sub_df = pd.read_csv(fpath, on_bad_lines='skip', encoding='latin1', low_memory=False)
                                            st.dataframe(sub_df, use_container_width=True)
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
                    else:
                         st.warning("No valid data rows found.")
                         
                    if misses:
                        with st.expander("See Missed Files"):
                            st.write(misses)

# ==========================================
# TAB 3: BANK LETTERS (Excel -> Bank Letters)
# ==========================================
with bank_tab:
    st.header("🏦 Bank Transaction Letter Generator")
    st.info("Upload the transaction Excel file to generate bank-specific letters for different transaction types.")
    
    # Initialize Bank Letter Processor
    if 'bank_processor' not in st.session_state:
        from backend import BankLetterProcessor
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
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Money Transfers", len(sheets['Money Transfer to']))
            with col2:
                st.metric("On Hold", len(sheets['Transaction put on hold']))
            with col3:
                st.metric("ATM Withdrawals", len(sheets['Withdrawal through ATM']))
            with col4:
                st.metric("Cheque Withdrawals", len(sheets['Cash Withdrawal through Cheque']))
            
            # Layer Detection for Sheet 1
            max_layers = processor.get_available_layers(sheets['Money Transfer to'])
            
            st.write("---")
            st.subheader("⚙️ Configuration")
            
            # Sheet Selection
            st.write("**Select Transaction Types to Process:**")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            
            with col_s1:
                process_sheet1 = st.checkbox("Money Transfer", value=True, key="proc_s1")
            with col_s2:
                process_sheet2 = st.checkbox("On Hold", value=True, key="proc_s2")
            with col_s3:
                process_sheet3 = st.checkbox("ATM", value=True, key="proc_s3")
            with col_s4:
                process_sheet4 = st.checkbox("Cheque", value=True, key="proc_s4")
            
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
                    total_tasks = sum([process_sheet1, process_sheet2, process_sheet3, process_sheet4])
                    current_task = 0
                    
                    try:
                        # Sheet 1: Money Transfer
                        if process_sheet1:
                            st.write("📝 Processing Money Transfer transactions...")
                            files = processor.generate_layerwise_letters(
                                sheets['Money Transfer to'], 
                                num_layers
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 2: On Hold
                        if process_sheet2:
                            st.write("📝 Processing Transaction On Hold...")
                            files = processor.generate_money_release_letters(
                                sheets['Transaction put on hold']
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 3: ATM
                        if process_sheet3:
                            st.write("📝 Processing ATM Withdrawals...")
                            files = processor.generate_atm_letters(
                                sheets['Withdrawal through ATM']
                            )
                            all_generated_files.extend(files)
                            current_task += 1
                            progress_bar.progress(current_task / total_tasks)
                        
                        # Sheet 4: Cheque
                        if process_sheet4:
                            st.write("📝 Processing Cheque Withdrawals...")
                            files = processor.generate_cheque_letters(
                                sheets['Cash Withdrawal through Cheque']
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
                                            st.download_button(
                                                label="📥 Download",
                                                data=f,
                                                file_name=file_name,
                                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                key=f"dl_bank_{idx}_{file_name}"
                                            )
                                
                                st.write("---")
