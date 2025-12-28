"""
Cell Tower Database Module
Lookup cell tower locations from Cell ID using open-source databases
"""

import requests
import pandas as pd
import logging
from typing import Optional, Tuple, Dict
import json
import os

logger = logging.getLogger(__name__)


class CellTowerDatabase:
    """
    Cell tower location lookup using open-source databases
    
    Supported databases:
    1. OpenCelliD (https://opencellid.org/) - Free API with registration
    2. Mozilla Location Service (MLS) - Free, no registration
    3. Unwired Labs (https://unwiredlabs.com/) - Free tier available
    """
    
    def __init__(self, cache_file: str = "cell_tower_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        # API keys (optional - set via environment or config)
        self.opencellid_key = os.environ.get('OPENCELLID_API_KEY', '')
        self.unwired_key = os.environ.get('UNWIRED_API_KEY', '')
    
    def _load_cache(self) -> Dict:
        """Load cached cell tower data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def parse_cell_id(self, cell_id_str: str) -> Optional[Dict]:
        """
        Parse Cell ID string into components
        
        Supports two formats:
        1. Airtel format (hyphenated): MCC-MNC-LAC-CellID
           Example: 404-96-290-128686112
        
        2. Jio format (concatenated): MCCMNC + LAC/CellID combined
           Example: 4058722113210
           - MCC: 405 (India - Jio)
           - MNC: 872 (Jio network code)
           - Remaining digits: LAC + Cell ID
        
        Returns:
            dict with mcc, mnc, lac, cell_id
        """
        if pd.isna(cell_id_str) or cell_id_str == '---':
            return None
        
        cell_id_str = str(cell_id_str).strip().replace("'", "")
        
        try:
            # Format 1: Airtel hyphenated format (404-96-290-128686112)
            if '-' in cell_id_str:
                parts = cell_id_str.split('-')
                if len(parts) >= 4:
                    return {
                        'mcc': int(parts[0]),  # Mobile Country Code
                        'mnc': int(parts[1]),  # Mobile Network Code
                        'lac': int(parts[2]),  # Location Area Code
                        'cell_id': int(parts[3])  # Cell ID
                    }
            
            # Format 2: Jio concatenated format (4058722113210 or 40587201f9011)
            # Jio uses MCC 405 (3 digits) + MNC (2-3 digits) + LAC/CellID
            # Note: Jio LTE cell IDs may contain hexadecimal characters (a-f)
            elif len(cell_id_str) >= 10:
                # Check if it starts with 405 (Jio MCC)
                if cell_id_str.startswith('405'):
                    # MCC: first 3 digits (405)
                    mcc = int(cell_id_str[0:3])
                    
                    # MNC: next 2-3 digits (common Jio MNCs: 840-874, 08-10, etc.)
                    # Try 3-digit MNC first (most common for Jio)
                    if len(cell_id_str) >= 13:
                        mnc = int(cell_id_str[3:6])
                        remaining = cell_id_str[6:]
                    else:
                        # Try 2-digit MNC
                        mnc = int(cell_id_str[3:5])
                        remaining = cell_id_str[5:]
                    
                    # Check if remaining contains hexadecimal characters
                    # If so, convert from hex to decimal
                    if any(c in 'abcdefABCDEF' for c in remaining):
                        # Hexadecimal format (LTE cell ID)
                        try:
                            # Convert entire hex string to decimal
                            cell_id_decimal = int(remaining, 16)
                            
                            # For LTE, the cell ID is typically the full value
                            # LAC in LTE is called TAC (Tracking Area Code)
                            # We'll use a simplified approach: upper bits = TAC, lower bits = Cell ID
                            lac = (cell_id_decimal >> 8) & 0xFFFF  # Upper 16 bits
                            cell_id = cell_id_decimal & 0xFF  # Lower 8 bits
                            
                            return {
                                'mcc': mcc,
                                'mnc': mnc,
                                'lac': lac,
                                'cell_id': cell_id
                            }
                        except ValueError:
                            logger.debug(f"Failed to parse hex cell ID: {remaining}")
                            return None
                    else:
                        # Numeric format
                        # Split remaining into LAC and Cell ID
                        # Typically LAC is 4-5 digits, Cell ID is the rest
                        if len(remaining) >= 6:
                            # Assume LAC is first 3-4 digits, Cell ID is the rest
                            lac_len = len(remaining) // 2
                            lac = int(remaining[:lac_len])
                            cell_id = int(remaining[lac_len:])
                        else:
                            # Short format - use first half as LAC
                            mid = len(remaining) // 2
                            lac = int(remaining[:mid]) if mid > 0 else 0
                            cell_id = int(remaining[mid:]) if mid < len(remaining) else 0
                        
                        return {
                            'mcc': mcc,
                            'mnc': mnc,
                            'lac': lac,
                            'cell_id': cell_id
                        }
                
                # Check if it starts with 404 (other Indian operators)
                elif cell_id_str.startswith('404'):
                    mcc = int(cell_id_str[0:3])
                    mnc = int(cell_id_str[3:5])
                    remaining = cell_id_str[5:]
                    
                    mid = len(remaining) // 2
                    lac = int(remaining[:mid]) if mid > 0 else 0
                    cell_id = int(remaining[mid:]) if mid < len(remaining) else 0
                    
                    return {
                        'mcc': mcc,
                        'mnc': mnc,
                        'lac': lac,
                        'cell_id': cell_id
                    }
        
        except Exception as e:
            logger.debug(f"Error parsing cell ID '{cell_id_str}': {e}")
        
        return None

    
    def lookup_opencellid(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[Tuple[float, float]]:
        """
        Lookup cell tower location using OpenCelliD API
        
        Note: Requires API key from https://opencellid.org/
        Free tier: 1000 requests/day
        """
        if not self.opencellid_key:
            return None
        
        cache_key = f"opencellid_{mcc}_{mnc}_{lac}_{cell_id}"
        if cache_key in self.cache:
            return tuple(self.cache[cache_key])
        
        try:
            url = "https://opencellid.org/cell/get"
            params = {
                'key': self.opencellid_key,
                'mcc': mcc,
                'mnc': mnc,
                'lac': lac,
                'cellid': cell_id,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'lat' in data and 'lon' in data:
                    lat, lon = float(data['lat']), float(data['lon'])
                    self.cache[cache_key] = [lat, lon]
                    self._save_cache()
                    return (lat, lon)
        except Exception as e:
            logger.error(f"OpenCelliD lookup error: {e}")
        
        return None
    
    def lookup_mozilla_mls(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[Tuple[float, float]]:
        """
        Lookup cell tower location using Mozilla Location Service
        
        Note: Free, no API key required
        Database: https://location.services.mozilla.com/
        """
        cache_key = f"mls_{mcc}_{mnc}_{lac}_{cell_id}"
        if cache_key in self.cache:
            return tuple(self.cache[cache_key])
        
        try:
            url = "https://location.services.mozilla.com/v1/geolocate?key=test"
            
            payload = {
                "cellTowers": [{
                    "radioType": "gsm",  # or "lte", "wcdma"
                    "mobileCountryCode": mcc,
                    "mobileNetworkCode": mnc,
                    "locationAreaCode": lac,
                    "cellId": cell_id
                }]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'location' in data:
                    lat = data['location']['lat']
                    lon = data['location']['lng']
                    self.cache[cache_key] = [lat, lon]
                    self._save_cache()
                    return (lat, lon)
        except Exception as e:
            logger.error(f"Mozilla MLS lookup error: {e}")
        
        return None
    
    def lookup_unwired_labs(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[Tuple[float, float]]:
        """
        Lookup cell tower location using Unwired Labs API
        
        Note: Requires API key from https://unwiredlabs.com/
        Free tier: 100 requests/day
        """
        if not self.unwired_key:
            return None
        
        cache_key = f"unwired_{mcc}_{mnc}_{lac}_{cell_id}"
        if cache_key in self.cache:
            return tuple(self.cache[cache_key])
        
        try:
            url = "https://us1.unwiredlabs.com/v2/process.php"
            
            payload = {
                "token": self.unwired_key,
                "radio": "gsm",
                "mcc": mcc,
                "mnc": mnc,
                "cells": [{
                    "lac": lac,
                    "cid": cell_id
                }],
                "address": 1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    lat = data['lat']
                    lon = data['lon']
                    self.cache[cache_key] = [lat, lon]
                    self._save_cache()
                    return (lat, lon)
        except Exception as e:
            logger.error(f"Unwired Labs lookup error: {e}")
        
        return None
    
    def lookup_cell_tower(self, cell_id_str: str) -> Optional[Tuple[float, float]]:
        """
        Lookup cell tower location using all available databases
        
        Tries in order:
        1. Cache
        2. Mozilla MLS (free, no key)
        3. OpenCelliD (if API key available)
        4. Unwired Labs (if API key available)
        
        Args:
            cell_id_str: Cell ID string (e.g., "404-96-290-128686112")
        
        Returns:
            (lat, lon) tuple or None
        """
        parsed = self.parse_cell_id(cell_id_str)
        if not parsed:
            return None
        
        mcc = parsed['mcc']
        mnc = parsed['mnc']
        lac = parsed['lac']
        cell_id = parsed['cell_id']
        
        # Try Mozilla MLS first (free, no key required)
        result = self.lookup_mozilla_mls(mcc, mnc, lac, cell_id)
        if result:
            return result
        
        # Try OpenCelliD if API key available
        if self.opencellid_key:
            result = self.lookup_opencellid(mcc, mnc, lac, cell_id)
            if result:
                return result
        
        # Try Unwired Labs if API key available
        if self.unwired_key:
            result = self.lookup_unwired_labs(mcc, mnc, lac, cell_id)
            if result:
                return result
        
        return None
    
    def enrich_cdr_with_cell_towers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich CDR dataframe with cell tower locations
        
        Adds columns:
        - Cell_Tower_Lat
        - Cell_Tower_Long
        - Cell_Tower_Source (which database provided the data)
        
        Supports both:
        - Airtel format: 'First CGI' column
        - Jio format: 'First Cell ID' column
        """
        df = df.copy()
        
        # Initialize new columns
        df['Cell_Tower_Lat'] = None
        df['Cell_Tower_Long'] = None
        df['Cell_Tower_Source'] = None
        
        # Determine which column to use
        cell_column = None
        if 'First CGI' in df.columns:
            cell_column = 'First CGI'
        elif 'First Cell ID' in df.columns:
            cell_column = 'First Cell ID'
        
        if cell_column:
            unique_cells = df[cell_column].dropna().unique()
            
            logger.info(f"Looking up {len(unique_cells)} unique cell towers from '{cell_column}' column...")
            
            successful_lookups = 0
            for i, cell_id in enumerate(unique_cells):
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(unique_cells)} cell towers processed...")
                
                result = self.lookup_cell_tower(cell_id)
                
                if result:
                    lat, lon = result
                    mask = df[cell_column] == cell_id
                    df.loc[mask, 'Cell_Tower_Lat'] = lat
                    df.loc[mask, 'Cell_Tower_Long'] = lon
                    df.loc[mask, 'Cell_Tower_Source'] = 'Database'
                    successful_lookups += 1
            
            logger.info(f"Successfully looked up {successful_lookups}/{len(unique_cells)} cell towers")
        else:
            logger.warning("No cell ID column found (expected 'First CGI' or 'First Cell ID')")
        
        return df
    
    def get_database_info(self) -> Dict:
        """Get information about available databases"""
        return {
            'mozilla_mls': {
                'name': 'Mozilla Location Service',
                'url': 'https://location.services.mozilla.com/',
                'api_key_required': False,
                'free': True,
                'rate_limit': 'Unlimited (fair use)',
                'coverage': 'Global',
                'status': 'Available'
            },
            'opencellid': {
                'name': 'OpenCelliD',
                'url': 'https://opencellid.org/',
                'api_key_required': True,
                'free': True,
                'rate_limit': '1000/day (free tier)',
                'coverage': 'Global',
                'status': 'Available' if self.opencellid_key else 'API key not configured'
            },
            'unwired_labs': {
                'name': 'Unwired Labs',
                'url': 'https://unwiredlabs.com/',
                'api_key_required': True,
                'free': True,
                'rate_limit': '100/day (free tier)',
                'coverage': 'Global',
                'status': 'Available' if self.unwired_key else 'API key not configured'
            }
        }
