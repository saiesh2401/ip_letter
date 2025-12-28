"""
Network Analysis Module
Analyzes contact networks and relationships from CDR data
"""

import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """Analyze contact networks from CDR data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.graph = None
        
    def build_network_graph(self, min_interactions: int = 1) -> nx.Graph:
        """Build network graph of contacts"""
        G = nx.Graph()
        
        # Get target number - use metadata if available, otherwise use first calling party
        target = 'Target' # Default target name
        if 'Target No' in self.df.columns and len(self.df) > 0:
            target = self.df['Target No'].iloc[0]
        elif 'Calling Party Telephone Number' in self.df.columns and len(self.df) > 0:
            # For Jio format, get the most common calling party (likely the target)
            target = self.df['Calling Party Telephone Number'].mode()[0]
        
        # Add target as central node
        G.add_node(target, node_type='target', size=100)
        
        # Determine the column for contacts based on available columns
        contact_column = None
        if 'B_Party_Clean' in self.df.columns:
            contact_column = 'B_Party_Clean'
        elif 'Called Party Telephone Number' in self.df.columns:
            contact_column = 'Called Party Telephone Number'
        
        if contact_column is None:
            logger.warning("Could not identify a contact column (e.g., 'B_Party_Clean' or 'Called Party Telephone Number'). Network graph will be empty.")
            self.graph = G
            return G

        # Count interactions per contact
        contact_counts = self.df[contact_column].value_counts()
        
        # Add edges for each contact
        for contact, count in contact_counts.items():
            if count >= min_interactions and contact != 'Unknown':
                G.add_node(contact, node_type='contact', size=count)
                G.add_edge(target, contact, weight=count)
        
        self.graph = G
        return G
    
    def get_network_metrics(self) -> Dict:
        """Calculate network metrics"""
        if self.graph is None:
            self.build_network_graph()
        
        metrics = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
        }
        
        # Degree centrality
        if self.graph.number_of_nodes() > 0:
            degree_cent = nx.degree_centrality(self.graph)
            metrics['top_central_contacts'] = dict(sorted(
                degree_cent.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
        
        return metrics
    
    def find_common_contacts(self, other_cdr_df: pd.DataFrame) -> List[str]:
        """Find contacts common between two CDRs"""
        # Determine contact column
        col1 = 'B_Party_Clean' if 'B_Party_Clean' in self.df.columns else 'Called Party Telephone Number'
        col2 = 'B_Party_Clean' if 'B_Party_Clean' in other_cdr_df.columns else 'Called Party Telephone Number'
        
        contacts_1 = set(self.df[col1].unique())
        contacts_2 = set(other_cdr_df[col2].unique())
        
        common = contacts_1.intersection(contacts_2)
        return list(common - {'Unknown'})
    
    def get_contact_timeline(self, contact: str) -> pd.DataFrame:
        """Get timeline of interactions with a specific contact"""
        # Determine contact column
        contact_col = 'B_Party_Clean' if 'B_Party_Clean' in self.df.columns else 'Called Party Telephone Number'
        
        contact_df = self.df[self.df[contact_col] == contact].copy()
        contact_df = contact_df.sort_values('DateTime')
        
        # Return available columns
        cols = ['DateTime', 'Call Type', 'Dur(s)']
        if 'First CGI Lat/Long' in contact_df.columns:
            cols.append('First CGI Lat/Long')
        
        return contact_df[cols]
    
    def cluster_contacts(self) -> Dict:
        """Cluster contacts based on interaction patterns"""
        clusters = {
            'very_frequent': [],  # 20+ interactions
            'frequent': [],       # 10-19 interactions
            'moderate': [],       # 5-9 interactions
            'occasional': [],     # 2-4 interactions
            'one_time': []        # 1 interaction
        }
        
        # Determine contact column
        contact_col = 'B_Party_Clean' if 'B_Party_Clean' in self.df.columns else 'Called Party Telephone Number'
        contact_counts = self.df[contact_col].value_counts()
        
        for contact, count in contact_counts.items():
            if contact == 'Unknown':
                continue
            
            if count >= 20:
                clusters['very_frequent'].append({'contact': contact, 'count': int(count)})
            elif count >= 10:
                clusters['frequent'].append({'contact': contact, 'count': int(count)})
            elif count >= 5:
                clusters['moderate'].append({'contact': contact, 'count': int(count)})
            elif count >= 2:
                clusters['occasional'].append({'contact': contact, 'count': int(count)})
            else:
                clusters['one_time'].append({'contact': contact, 'count': int(count)})
        
        return clusters
