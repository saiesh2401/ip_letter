import pandas as pd
import io

# User provided content
raw_content = """BHARTI AIRTEL LTD

Pan India

DSL IPDR OF PUBLIC IP4: 122.162.191.215 from 06-Sep-2025 14:39:48 to 06-Sep-2025 14:39:48

DSL_User_ID,Event_Start_Time,Session_Start_Time,Session_End_Time,Duration(seconds), Uplink_Vol,Downlink_Vol,Source_public_Ipv4,Source_Public_IPv6,Source_Public_Port,Destination_Ipv4,Destination_Ipv6,Destination_Port,Source_Private_Ipv4,Source_Private_Port, mac_address, User_Type
074421640411_wifi,,'04-Sep-2025 18:50:33','06-Sep-2025 15:30:00',158400,1391679449,1926503582,122.162.191.215,,,,,,122.162.191.215,,,static
074421640411_wifi,,'04-Sep-2025 18:50:33','06-Sep-2025 15:30:00',,,,122.162.191.215,,,,,,122.162.191.215,,,static

 This is System generated report, and needs no signature.

 04-Nov-2025 06:06:24"""

def test_parse():
    print("Testing Parsing Logic...")
    
    # 1. Simulate reading lines
    lines = raw_content.split('\n')
    
    # 2. Find Header
    header_idx = -1
    for i, line in enumerate(lines[:20]):
        if "DSL_User_ID" in line:
            header_idx = i
            print(f"Terms Found at Line Index: {header_idx}")
            break
            
    if header_idx != -1:
        # Debug Counts
        header_line = lines[header_idx]
        data_line_1 = lines[header_idx+1]
        
        print(f"Header Line: {header_line}")
        print(f"Header Comma Count: {header_line.count(',')}")
        print(f"Data Line 1: {data_line_1}")
        print(f"Data 1 Comma Count: {data_line_1.count(',')}")

        # 3. Parse with Pandas
        # Simulating file object
        f_obj = io.StringIO(raw_content)
        try:
            # Removed on_bad_lines='skip' to see the actual error
            # Trying engine='python' and explicit sep
            df = pd.read_csv(f_obj, skiprows=header_idx, header=0, quotechar="'", skipinitialspace=True, sep=',', engine='python')
            print("\n--- Parsing Successful ---")
            print(f"Rows Found: {len(df)}")
            print("Columns:", list(df.columns))
            print("\nContent:\n", df.to_string())
        except Exception as e:
            print(f"Parsing Failed: {e}")

if __name__ == "__main__":
    test_parse()
