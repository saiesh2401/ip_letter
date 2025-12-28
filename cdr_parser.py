"""
CDR Parser Module
Handles parsing of multiple CDR formats (Airtel, Jio) and data extraction
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CDRParser:
    """Parse and process Call Detail Records from multiple formats (Airtel, Jio)"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_data = None
        self.parsed_data = None
        self.metadata = {}
        self.format_type = None  # 'airtel' or 'jio'
        
    def parse(self) -> pd.DataFrame:
        """Parse the CDR file and return structured data"""
        try:
            # Read the file to extract metadata and detect format
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Detect format type
            self.format_type = self._detect_format(lines)
            logger.info(f"Detected CDR format: {self.format_type.upper()}")
            
            # Extract metadata from header
            self._extract_metadata(lines)
            
            # Parse based on format
            if self.format_type == 'airtel':
                self.parsed_data = self._parse_airtel(lines)
            elif self.format_type == 'jio':
                self.parsed_data = self._parse_jio(lines)
            else:
                raise ValueError(f"Unsupported CDR format: {self.format_type}")
            
            logger.info(f"Successfully parsed {len(self.parsed_data)} records from {self.format_type.upper()} CDR")
            return self.parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing CDR file: {str(e)}")
            raise
    
    def _detect_format(self, lines: List[str]) -> str:
        """Detect CDR format type"""
        # Check for Airtel indicators
        for line in lines[:20]:
            if 'BHARTI AIRTEL' in line.upper():
                return 'airtel'
            if 'Target No' in line and 'Call Type' in line:
                return 'airtel'
        
        # Check for Jio indicators
        for line in lines[:20]:
            if 'Calling Party Telephone Number' in line:
                return 'jio'
            if 'Ticket Number' in line:
                return 'jio'
        
        # Default to airtel if can't detect
        logger.warning("Could not detect format, defaulting to Airtel")
        return 'airtel'
    
    def _extract_metadata(self, lines: List[str]) -> None:
        """Extract metadata from file header"""
        # Airtel metadata
        for line in lines[:10]:
            if 'Call Details of Mobile No' in line:
                match = re.search(r"'(\d+)'.*'(.+?)'.*'(.+?)'", line)
                if match:
                    self.metadata['target_number'] = match.group(1)
                    self.metadata['start_date'] = match.group(2)
                    self.metadata['end_date'] = match.group(3)
            
            if 'BHARTI AIRTEL' in line or 'AIRTEL' in line:
                self.metadata['operator'] = 'Airtel'
        
        # Jio metadata
        for line in lines[:20]:
            if 'Input Value' in line and 'MSISDN' in line:
                match = re.search(r"'(\d+)'", line)
                if match:
                    self.metadata['target_number'] = match.group(1)
            
            if 'Date Range' in line:
                match = re.search(r'(\d{4}-\d{2}-\d{2}.*?) to (\d{4}-\d{2}-\d{2})', line)
                if match:
                    self.metadata['start_date'] = match.group(1)
                    self.metadata['end_date'] = match.group(2)
            
            if 'Total Records' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    self.metadata['total_records'] = match.group(1)
                    self.metadata['operator'] = 'Jio'
    
    def _parse_airtel(self, lines: List[str]) -> pd.DataFrame:
        """Parse Airtel format CDR"""
        # Find the header row
        header_row = None
        for i, line in enumerate(lines):
            if 'Target No' in line and 'Call Type' in line:
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("Could not find header row in Airtel CDR file")
        
        # Read the actual data
        df = pd.read_csv(
            self.file_path,
            skiprows=header_row,
            encoding='utf-8',
            on_bad_lines='skip'
        )
        
        # Clean and process
        df = self._clean_airtel_data(df)
        return df
    
    def _parse_jio(self, lines: List[str]) -> pd.DataFrame:
        """Parse Jio format CDR"""
        # Find the header row
        header_row = None
        for i, line in enumerate(lines):
            if 'Calling Party Telephone Number' in line:
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("Could not find header row in Jio CDR file")
        
        # Read the actual data
        df = pd.read_csv(
            self.file_path,
            skiprows=header_row,
            encoding='utf-8',
            on_bad_lines='skip'
        )
        
        # Clean and process
        df = self._clean_jio_data(df)
        return df
    
    def _clean_airtel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process Airtel CDR data"""
        df = df.copy()
        
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Parse datetime
        df['Date'] = df['Date'].astype(str).str.strip().str.strip("'\"")
        df['Time'] = df['Time'].astype(str).str.strip().str.strip("'\"")
        
        df['DateTime'] = pd.to_datetime(
            df['Date'] + ' ' + df['Time'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        
        # Fallback for rows without time
        mask = df['DateTime'].isna()
        if mask.any():
            df.loc[mask, 'DateTime'] = pd.to_datetime(
                df.loc[mask, 'Date'],
                format='%d/%m/%Y',
                errors='coerce'
            )
        
        # Drop rows with invalid datetime
        initial_count = len(df)
        df = df.dropna(subset=['DateTime'])
        dropped = initial_count - len(df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} records due to invalid datetime")
        
        # Extract temporal features
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.day_name()
        df['Date_Only'] = df['DateTime'].dt.date
        df['TimePeriod'] = df['Hour'].apply(self._classify_time_period)
        
        # Parse duration
        df['Dur(s)'] = pd.to_numeric(df['Dur(s)'], errors='coerce').fillna(0).astype(int)
        
        # Parse coordinates
        coords_first = df['First CGI Lat/Long'].apply(self._parse_coordinates)
        df['First_Lat'] = coords_first.apply(lambda x: x[0] if x else None)
        df['First_Long'] = coords_first.apply(lambda x: x[1] if x else None)
        
        coords_last = df['Last CGI Lat/Long'].apply(self._parse_coordinates)
        df['Last_Lat'] = coords_last.apply(lambda x: x[0] if x else None)
        df['Last_Long'] = coords_last.apply(lambda x: x[1] if x else None)
        
        # Clean B Party number
        df['B_Party_Clean'] = df['B Party No'].apply(self._clean_phone_number)
        
        # Classify call type
        df['Call_Category'] = df['Call Type'].apply(self._classify_call_type)
        
        # Add time flags
        df['Is_Night'] = df['Hour'].apply(lambda x: 1 if (x >= 22 or x < 6) else 0)
        df['Is_Day'] = df['Hour'].apply(lambda x: 1 if (6 <= x < 18) else 0)
        df['Is_Evening'] = df['Hour'].apply(lambda x: 1 if (18 <= x < 22) else 0)
        
        # Standardize column names for universal access
        df['Call Type'] = df['Call Type']  # Already exists
        
        return df
    
    def _clean_jio_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process Jio CDR data"""
        df = df.copy()
        
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Parse datetime - Jio format: DD/MM/YYYY HH:MM:SS
        df['Call Date'] = df['Call Date'].astype(str).str.strip()
        df['Call Time'] = df['Call Time'].astype(str).str.strip()
        
        df['DateTime'] = pd.to_datetime(
            df['Call Date'] + ' ' + df['Call Time'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        
        # Fallback for rows without time
        mask = df['DateTime'].isna()
        if mask.any():
            df.loc[mask, 'DateTime'] = pd.to_datetime(
                df.loc[mask, 'Call Date'],
                format='%d/%m/%Y',
                errors='coerce'
            )
        
        # Drop rows with invalid datetime
        initial_count = len(df)
        df = df.dropna(subset=['DateTime'])
        dropped = initial_count - len(df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} records due to invalid datetime")
        
        # Extract temporal features
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.day_name()
        df['Date_Only'] = df['DateTime'].dt.date
        df['TimePeriod'] = df['Hour'].apply(self._classify_time_period)
        
        # Parse duration
        df['Dur(s)'] = pd.to_numeric(df['Call Duration'], errors='coerce').fillna(0).astype(int)
        
        # Jio doesn't have GPS coordinates, set to None
        df['First_Lat'] = None
        df['First_Long'] = None
        df['Last_Lat'] = None
        df['Last_Long'] = None
        
        # Store Cell IDs for later lookup
        df['First CGI'] = df['First Cell ID'].astype(str)
        df['Last CGI'] = df['Last Cell ID'].astype(str)
        
        # Clean B Party number - Jio uses "Called Party Telephone Number"
        df['B_Party_Clean'] = df['Called Party Telephone Number'].apply(self._clean_phone_number)
        
        # Classify call type - Jio uses different naming
        df['Call_Category'] = df['Call Type'].apply(self._classify_jio_call_type)
        
        # Add time flags
        df['Is_Night'] = df['Hour'].apply(lambda x: 1 if (x >= 22 or x < 6) else 0)
        df['Is_Day'] = df['Hour'].apply(lambda x: 1 if (6 <= x < 18) else 0)
        df['Is_Evening'] = df['Hour'].apply(lambda x: 1 if (18 <= x < 22) else 0)
        
        # Standardize column names for universal access
        df['Call Type'] = df['Call Type']  # Keep original
        df['B Party No'] = df['Called Party Telephone Number']  # Standardize
        df['Date'] = df['Call Date']  # Standardize
        df['Time'] = df['Call Time']  # Standardize
        
        return df
    
    @staticmethod
    def _classify_time_period(hour: int) -> str:
        """Classify hour into time period"""
        if pd.isna(hour):
            return 'Unknown'
        if 0 <= hour < 6:
            return 'Late Night (00:00-06:00)'
        elif 6 <= hour < 12:
            return 'Morning (06:00-12:00)'
        elif 12 <= hour < 18:
            return 'Afternoon (12:00-18:00)'
        elif 18 <= hour < 22:
            return 'Evening (18:00-22:00)'
        else:
            return 'Night (22:00-00:00)'
    
    @staticmethod
    def _parse_coordinates(coord_str: str) -> Tuple[Optional[float], Optional[float]]:
        """Parse coordinate string into lat/long tuple"""
        if pd.isna(coord_str) or coord_str == '':
            return None, None
        
        try:
            parts = str(coord_str).split('/')
            if len(parts) == 2:
                return float(parts[0]), float(parts[1])
        except:
            pass
        
        return None, None
    
    @staticmethod
    def _clean_phone_number(number: str) -> str:
        """Clean and standardize phone number"""
        if pd.isna(number):
            return 'Unknown'
        
        # Remove non-numeric characters except for special prefixes
        number = str(number).strip().strip("'\"")
        
        # Keep special identifiers (AD-, AH-, CP-, JD-, etc.)
        if '-' in number and not number[0].isdigit():
            return number
        
        # Extract only digits
        digits = re.sub(r'\D', '', number)
        
        # Return standardized format
        if len(digits) >= 10:
            return digits[-10:]  # Last 10 digits
        
        return number
    
    @staticmethod
    def _classify_call_type(call_type: str) -> str:
        """Classify Airtel call type into broader categories"""
        if pd.isna(call_type):
            return 'Unknown'
        
        call_type = str(call_type).upper()
        
        if 'IN' in call_type:
            return 'Incoming Call'
        elif 'OUT' in call_type:
            return 'Outgoing Call'
        elif 'SMT' in call_type or 'SMS' in call_type:
            return 'SMS Received'
        elif 'SMO' in call_type:
            return 'SMS Sent'
        else:
            return 'Other'
    
    @staticmethod
    def _classify_jio_call_type(call_type: str) -> str:
        """Classify Jio call type into broader categories"""
        if pd.isna(call_type):
            return 'Unknown'
        
        call_type = str(call_type).upper()
        
        if 'A_IN' in call_type:
            return 'Incoming Call'
        elif 'A_OUT' in call_type:
            return 'Outgoing Call'
        elif 'SMSIN' in call_type or 'P2P_SMSIN' in call_type or 'A2P_SMSIN' in call_type:
            return 'SMS Received'
        elif 'SMSOUT' in call_type or 'P2AOUT' in call_type:
            return 'SMS Sent'
        else:
            return 'Other'
    
    def get_summary(self) -> Dict:
        """Get summary statistics of the CDR"""
        if self.parsed_data is None:
            return {}
        
        df = self.parsed_data
        
        return {
            'format': self.format_type,
            'total_records': len(df),
            'date_range': {
                'start': df['DateTime'].min(),
                'end': df['DateTime'].max()
            },
            'call_types': df['Call Type'].value_counts().to_dict(),
            'unique_contacts': df['B_Party_Clean'].nunique(),
            'total_duration': df['Dur(s)'].sum(),
            'avg_duration': df['Dur(s)'].mean(),
            'night_activity': df['Is_Night'].sum(),
            'day_activity': df['Is_Day'].sum(),
        }
