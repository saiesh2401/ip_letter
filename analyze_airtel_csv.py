import os

CSV_PATH = "Airtel_Reply/Extracted/public_ip4_106.194.171.140/public_ip4_106.194.171.140_1.csv"

def analyze():
    print(f"Reading Raw Lines from {CSV_PATH}")
    try:
        with open(CSV_PATH, "rb") as f: # Binary to avoid encoding crash
            lines = f.readlines()
            
        print(f"Total Lines: {len(lines)}")
        print("-" * 30)
        for i, line in enumerate(lines[:20]):
            try:
                decoded = line.decode('utf-8').strip()
            except:
                decoded = line.decode('latin1').strip()
            print(f"{i}: {decoded}")
        print("-" * 30)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
