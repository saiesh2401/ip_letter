import zipfile
import os
import pandas as pd

ZIP_PATH = "Airtel_Reply/SR_1487808_1.zip"
EXTRACT_PATH = "Airtel_Reply/Extracted"
PASSWORD = b"18Imc"

def explore():
    if not os.path.exists(EXTRACT_PATH):
        os.makedirs(EXTRACT_PATH)
        
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            print(f"Extracting {ZIP_PATH}...")
            zf.extractall(path=EXTRACT_PATH, pwd=PASSWORD)
            
        print("\n--- Extracted Files ---")
        files = []
        for root, dirs, filenames in os.walk(EXTRACT_PATH):
            for f in filenames:
                full_path = os.path.join(root, f)
                print(f"Found: {f}")
                files.append(full_path)
                
        print("\n--- Recursive Extraction ---")
        for f in files:
            if f.endswith(".zip"):
                print(f"Unzipping Inner: {os.path.basename(f)}")
                inner_dir = os.path.join(EXTRACT_PATH, os.path.splitext(os.path.basename(f))[0])
                try:
                    with zipfile.ZipFile(f, 'r') as zf_inner:
                        # Try with password
                        try:
                            zf_inner.extractall(path=inner_dir, pwd=PASSWORD)
                            print(f"  > Extracted with password to {inner_dir}")
                        except:
                            # Try without password
                            zf_inner.extractall(path=inner_dir)
                            print(f"  > Extracted components (no password) to {inner_dir}")
                            
                    # List inner files
                    for root_i, _, files_i in os.walk(inner_dir):
                        for fi in files_i:
                             print(f"    - {fi}")
                             # If Excel, read header
                             if fi.endswith(".xls") or fi.endswith(".xlsx"):
                                 try:
                                     dx = pd.read_excel(os.path.join(root_i, fi))
                                     print(f"      Columns: {list(dx.columns)}")
                                 except: pass

                except Exception as e:
                    print(f"  > Failed: {e}")

        print("\n--- File Analysis ---")
                    
    except Exception as e:
        print(f"Error unzipping: {e}")

if __name__ == "__main__":
    explore()
