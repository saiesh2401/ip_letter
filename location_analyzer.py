"""
Location Analyzer Module
Location intelligence and movement pattern analysis
"""

import pandas as pd
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class LocationAnalyzer:
    """Analyze location patterns from tower data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Filter valid coordinates
        self.valid_df = df.dropna(subset=['First_Lat', 'First_Long'])
        
    def get_location_clusters(self) -> List[Dict]:
        """Get clusters of frequently visited locations"""
        if len(self.valid_df) == 0:
            return []
        
        location_counts = self.valid_df.groupby(['First_Lat', 'First_Long']).size()
        location_counts = location_counts.sort_values(ascending=False)
        
        clusters = []
        for (lat, lon), count in location_counts.items():
            clusters.append({
                'lat': float(lat),
                'lon': float(lon),
                'count': int(count),
                'percentage': float(count / len(self.valid_df) * 100)
            })
        
        return clusters
    
    def get_time_based_locations(self) -> Dict:
        """Get locations by time of day"""
        locations = {
            'night': [],
            'day': [],
            'evening': []
        }
        
        # Night locations
        night_df = self.valid_df[self.valid_df['Is_Night'] == 1]
        if len(night_df) > 0:
            night_locs = night_df.groupby(['First_Lat', 'First_Long']).size()
            locations['night'] = [
                {'lat': float(lat), 'lon': float(lon), 'count': int(count)}
                for (lat, lon), count in night_locs.nlargest(10).items()
            ]
        
        # Day locations
        day_df = self.valid_df[self.valid_df['Is_Day'] == 1]
        if len(day_df) > 0:
            day_locs = day_df.groupby(['First_Lat', 'First_Long']).size()
            locations['day'] = [
                {'lat': float(lat), 'lon': float(lon), 'count': int(count)}
                for (lat, lon), count in day_locs.nlargest(10).items()
            ]
        
        # Evening locations
        evening_df = self.valid_df[self.valid_df['Is_Evening'] == 1]
        if len(evening_df) > 0:
            evening_locs = evening_df.groupby(['First_Lat', 'First_Long']).size()
            locations['evening'] = [
                {'lat': float(lat), 'lon': float(lon), 'count': int(count)}
                for (lat, lon), count in evening_locs.nlargest(10).items()
            ]
        
        return locations
    
    def get_movement_timeline(self) -> List[Dict]:
        """Get chronological movement data"""
        if len(self.valid_df) == 0:
            return []
        
        timeline = []
        sorted_df = self.valid_df.sort_values('DateTime')
        
        for _, row in sorted_df.iterrows():
            timeline.append({
                'datetime': row['DateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'lat': float(row['First_Lat']),
                'lon': float(row['First_Long']),
                'call_type': row['Call_Category'],
                'contact': row['B_Party_Clean']
            })
        
        return timeline
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate approximate distance between two coordinates (in km)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
