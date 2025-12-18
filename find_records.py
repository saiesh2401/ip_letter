import os

EXTRACT_PATH = "Airtel_Reply/Extracted"

def find_data():
    print("Searching for valid records...")
    found_any = False
    
    for root, _, filenames in os.walk(EXTRACT_PATH):
        for f in filenames:
            if f.endswith(".csv"):
                # Read file
                path = os.path.join(root, f)
                try:
                    with open(path, "rb") as file:
                        lines = file.readlines()
                        
                    # Line 6 is Header, Line 7 is Data (0-indexed)
                    if len(lines) > 7:
                        # Decode headers and data
                        try:
                            header = lines[6].decode('utf-8').strip()
                            data = lines[7].decode('utf-8').strip()
                        except:
                            header = lines[6].decode('latin1').strip()
                            data = lines[7].decode('latin1').strip()
                            
                        if "No Records Found" not in data:
                            print("-" * 50)
                            print(f"FILE: {f}")
                            print(f"RAW DATA: {data}")
                            found_any = True
                            # Continue searching...
                except:
                    pass
    
    if not found_any:
        print("Scanned all files. All return 'No Records Found'.")

if __name__ == "__main__":
    find_data()
