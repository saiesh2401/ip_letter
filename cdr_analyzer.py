"""
CDR Analyzer Module
Advanced analytics and pattern detection for CDR data
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from typing import Dict, List, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class CDRAnalyzer:
    """Advanced analysis of Call Detail Records"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def get_temporal_analysis(self) -> Dict:
        """
        STATE-OF-THE-ART TEMPORAL ANALYSIS
        Comprehensive day/night and hourly pattern analysis
        """
        analysis = {}
        
        # === NIGHT vs DAY ANALYSIS ===
        night_calls = self.df[self.df['Is_Night'] == 1]
        day_calls = self.df[self.df['Is_Day'] == 1]
        evening_calls = self.df[self.df['Is_Evening'] == 1]
        
        analysis['night_day_summary'] = {
            'night_count': len(night_calls),
            'day_count': len(day_calls),
            'evening_count': len(evening_calls),
            'night_percentage': (len(night_calls) / len(self.df) * 100) if len(self.df) > 0 else 0,
            'day_percentage': (len(day_calls) / len(self.df) * 100) if len(self.df) > 0 else 0,
            'evening_percentage': (len(evening_calls) / len(self.df) * 100) if len(self.df) > 0 else 0,
        }
        
        # Night activity breakdown
        analysis['night_activity'] = {
            'late_night_00_03': len(self.df[(self.df['Hour'] >= 0) & (self.df['Hour'] < 3)]),
            'late_night_03_06': len(self.df[(self.df['Hour'] >= 3) & (self.df['Hour'] < 6)]),
            'night_22_00': len(self.df[(self.df['Hour'] >= 22)]),
            'top_night_contacts': self._get_top_contacts(night_calls, 10),
            'night_call_types': night_calls['Call_Category'].value_counts().to_dict(),
            'night_duration_total': int(night_calls['Dur(s)'].sum()),
            'night_duration_avg': float(night_calls['Dur(s)'].mean()) if len(night_calls) > 0 else 0,
        }
        
        # Day activity breakdown
        analysis['day_activity'] = {
            'morning_06_09': len(self.df[(self.df['Hour'] >= 6) & (self.df['Hour'] < 9)]),
            'morning_09_12': len(self.df[(self.df['Hour'] >= 9) & (self.df['Hour'] < 12)]),
            'afternoon_12_15': len(self.df[(self.df['Hour'] >= 12) & (self.df['Hour'] < 15)]),
            'afternoon_15_18': len(self.df[(self.df['Hour'] >= 15) & (self.df['Hour'] < 18)]),
            'top_day_contacts': self._get_top_contacts(day_calls, 10),
            'day_call_types': day_calls['Call_Category'].value_counts().to_dict(),
            'day_duration_total': int(day_calls['Dur(s)'].sum()),
            'day_duration_avg': float(day_calls['Dur(s)'].mean()) if len(day_calls) > 0 else 0,
        }
        
        # Hourly distribution
        hourly_dist = self.df.groupby('Hour').size().to_dict()
        analysis['hourly_distribution'] = {str(h): hourly_dist.get(h, 0) for h in range(24)}
        
        # Peak hours
        hourly_counts = self.df['Hour'].value_counts()
        analysis['peak_hours'] = {
            'overall': int(hourly_counts.idxmax()) if len(hourly_counts) > 0 else None,
            'night': int(night_calls['Hour'].value_counts().idxmax()) if len(night_calls) > 0 else None,
            'day': int(day_calls['Hour'].value_counts().idxmax()) if len(day_calls) > 0 else None,
        }
        
        # Suspicious patterns
        analysis['suspicious_patterns'] = self._detect_suspicious_temporal_patterns()
        
        return analysis
    
    def get_contact_analysis(self) -> Dict:
        """Analyze contact patterns and relationships"""
        analysis = {}
        
        # Top contacts overall
        contact_counts = self.df['B_Party_Clean'].value_counts()
        analysis['top_contacts'] = contact_counts.head(20).to_dict()
        
        # Contact frequency distribution
        analysis['contact_frequency'] = {
            'unique_contacts': int(self.df['B_Party_Clean'].nunique()),
            'one_time_contacts': int((contact_counts == 1).sum()),
            'frequent_contacts_5plus': int((contact_counts >= 5).sum()),
            'very_frequent_10plus': int((contact_counts >= 10).sum()),
        }
        
        # Call type breakdown by contact
        analysis['contact_call_types'] = {}
        for contact in contact_counts.head(10).index:
            contact_df = self.df[self.df['B_Party_Clean'] == contact]
            analysis['contact_call_types'][contact] = {
                'total': len(contact_df),
                'incoming': len(contact_df[contact_df['Call Type'] == 'IN']),
                'outgoing': len(contact_df[contact_df['Call Type'] == 'OUT']),
                'sms': len(contact_df[contact_df['Call Type'].str.contains('SM', na=False)]),
            }
        
        # New contacts over time
        analysis['new_contacts_timeline'] = self._analyze_new_contacts()
        
        return analysis
    
    def get_location_analysis(self) -> Dict:
        """Analyze location patterns from tower data"""
        analysis = {}
        
        # Filter records with valid coordinates
        valid_coords = self.df.dropna(subset=['First_Lat', 'First_Long'])
        
        if len(valid_coords) == 0:
            return {'error': 'No valid location data available'}
        
        # Unique locations
        unique_locations = valid_coords.groupby(['First_Lat', 'First_Long']).size()
        analysis['unique_towers'] = len(unique_locations)
        
        # Most frequent locations
        top_locations = unique_locations.nlargest(10)
        analysis['top_locations'] = [
            {
                'lat': float(lat),
                'lon': float(lon),
                'count': int(count),
                'percentage': float(count / len(valid_coords) * 100)
            }
            for (lat, lon), count in top_locations.items()
        ]
        
        # Night vs Day locations
        night_locs = self.df[self.df['Is_Night'] == 1].dropna(subset=['First_Lat', 'First_Long'])
        day_locs = self.df[self.df['Is_Day'] == 1].dropna(subset=['First_Lat', 'First_Long'])
        
        analysis['night_locations'] = len(night_locs.groupby(['First_Lat', 'First_Long']))
        analysis['day_locations'] = len(day_locs.groupby(['First_Lat', 'First_Long']))
        
        # Movement analysis
        analysis['movement_patterns'] = self._analyze_movement()
        
        return analysis
    
    def get_communication_patterns(self) -> Dict:
        """Analyze communication patterns and behaviors"""
        analysis = {}
        
        # Call duration analysis
        voice_calls = self.df[self.df['Dur(s)'] > 0]
        
        if len(voice_calls) > 0:
            analysis['duration_stats'] = {
                'total_duration_seconds': int(voice_calls['Dur(s)'].sum()),
                'total_duration_hours': float(voice_calls['Dur(s)'].sum() / 3600),
                'avg_duration': float(voice_calls['Dur(s)'].mean()),
                'median_duration': float(voice_calls['Dur(s)'].median()),
                'max_duration': int(voice_calls['Dur(s)'].max()),
                'short_calls_under_30s': int((voice_calls['Dur(s)'] < 30).sum()),
                'long_calls_over_5min': int((voice_calls['Dur(s)'] > 300).sum()),
            }
        
        # Daily activity patterns
        daily_counts = self.df.groupby('Date_Only').size()
        analysis['daily_patterns'] = {
            'avg_daily_activity': float(daily_counts.mean()),
            'max_daily_activity': int(daily_counts.max()),
            'min_daily_activity': int(daily_counts.min()),
            'active_days': int(len(daily_counts)),
        }
        
        # Burst detection (high activity periods)
        analysis['burst_activity'] = self._detect_burst_activity()
        
        # Weekly patterns
        dow_counts = self.df['DayOfWeek'].value_counts()
        analysis['day_of_week'] = dow_counts.to_dict()
        
        return analysis
    
    def get_device_analysis(self) -> Dict:
        """Analyze device and SIM usage patterns"""
        analysis = {}
        
        # IMEI analysis
        if 'IMEI' in self.df.columns:
            imei_counts = self.df['IMEI'].value_counts()
            analysis['imei_info'] = {
                'unique_devices': int(self.df['IMEI'].nunique()),
                'devices_used': imei_counts.to_dict(),
                'device_changes': self._detect_device_changes(),
            }
        
        # IMSI analysis
        if 'IMSI' in self.df.columns:
            imsi_counts = self.df['IMSI'].value_counts()
            analysis['imsi_info'] = {
                'unique_sims': int(self.df['IMSI'].nunique()),
                'sims_used': imsi_counts.to_dict(),
            }
        
        return analysis
    
    def _get_top_contacts(self, df: pd.DataFrame, n: int = 10) -> Dict:
        """Get top N contacts from a dataframe"""
        return df['B_Party_Clean'].value_counts().head(n).to_dict()
    
    def _detect_suspicious_temporal_patterns(self) -> Dict:
        """Detect suspicious temporal patterns"""
        patterns = {}
        
        # Excessive night activity
        night_pct = (self.df['Is_Night'].sum() / len(self.df) * 100) if len(self.df) > 0 else 0
        patterns['excessive_night_activity'] = night_pct > 30
        patterns['night_activity_percentage'] = float(night_pct)
        
        # Late night activity (00:00 - 04:00)
        late_night = len(self.df[(self.df['Hour'] >= 0) & (self.df['Hour'] < 4)])
        patterns['late_night_activity'] = late_night
        patterns['late_night_suspicious'] = late_night > 50
        
        # Consistent night contacts
        night_df = self.df[self.df['Is_Night'] == 1]
        if len(night_df) > 0:
            night_contacts = night_df['B_Party_Clean'].value_counts()
            patterns['frequent_night_contacts'] = night_contacts.head(5).to_dict()
        
        return patterns
    
    def _analyze_new_contacts(self) -> List[Dict]:
        """Analyze when new contacts appear"""
        timeline = []
        seen_contacts = set()
        
        for _, row in self.df.sort_values('DateTime').iterrows():
            contact = row['B_Party_Clean']
            if contact not in seen_contacts and contact != 'Unknown':
                seen_contacts.add(contact)
                timeline.append({
                    'date': row['DateTime'].strftime('%Y-%m-%d'),
                    'contact': contact,
                    'call_type': row['Call_Category']
                })
        
        return timeline[:50]  # Return first 50 new contacts
    
    def _analyze_movement(self) -> Dict:
        """Analyze movement between locations"""
        movement = {}
        
        # Calculate movements (when location changes)
        valid_df = self.df.dropna(subset=['First_Lat', 'First_Long']).sort_values('DateTime')
        
        if len(valid_df) > 1:
            # Detect location changes
            location_changes = 0
            prev_lat, prev_lon = None, None
            
            for _, row in valid_df.iterrows():
                curr_lat, curr_lon = row['First_Lat'], row['First_Long']
                if prev_lat is not None:
                    # Consider it a movement if coordinates differ significantly
                    if abs(curr_lat - prev_lat) > 0.01 or abs(curr_lon - prev_lon) > 0.01:
                        location_changes += 1
                prev_lat, prev_lon = curr_lat, curr_lon
            
            movement['total_movements'] = location_changes
            movement['mobility_score'] = float(location_changes / len(valid_df) * 100)
        
        return movement
    
    def _detect_burst_activity(self) -> List[Dict]:
        """Detect periods of unusually high activity"""
        bursts = []
        
        # Group by hour
        hourly_activity = self.df.groupby([self.df['DateTime'].dt.date, self.df['DateTime'].dt.hour]).size()
        
        # Find hours with activity > mean + 2*std
        mean_activity = hourly_activity.mean()
        std_activity = hourly_activity.std()
        threshold = mean_activity + 2 * std_activity
        
        burst_periods = hourly_activity[hourly_activity > threshold]
        
        for (date, hour), count in burst_periods.items():
            bursts.append({
                'date': str(date),
                'hour': int(hour),
                'count': int(count),
                'threshold': float(threshold)
            })
        
        return sorted(bursts, key=lambda x: x['count'], reverse=True)[:20]
    
    def _detect_device_changes(self) -> List[Dict]:
        """Detect when device (IMEI) changes"""
        changes = []
        
        if 'IMEI' not in self.df.columns:
            return changes
        
        sorted_df = self.df.sort_values('DateTime')
        prev_imei = None
        
        for _, row in sorted_df.iterrows():
            curr_imei = row['IMEI']
            if prev_imei is not None and curr_imei != prev_imei:
                changes.append({
                    'date': row['DateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'from_imei': prev_imei,
                    'to_imei': curr_imei
                })
            prev_imei = curr_imei
        
        return changes
