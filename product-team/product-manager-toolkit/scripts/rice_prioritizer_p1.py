# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rice_prioritizer_base import *  # noqa: F403,E402


class RICECalculator:
    """Calculate RICE scores for feature prioritization"""
    
    def __init__(self):
        self.impact_map = {
            'massive': 3.0,
            'high': 2.0,
            'medium': 1.0,
            'low': 0.5,
            'minimal': 0.25
        }
        
        self.confidence_map = {
            'high': 100,
            'medium': 80,
            'low': 50
        }
        
        self.effort_map = {
            'xl': 13,
            'l': 8,
            'm': 5,
            's': 3,
            'xs': 1
        }
    
    def calculate_rice(self, reach: int, impact: str, confidence: str, effort: str) -> float:
        """
        Calculate RICE score
        
        Args:
            reach: Number of users/customers affected per quarter
            impact: massive/high/medium/low/minimal
            confidence: high/medium/low (percentage)
            effort: xl/l/m/s/xs (person-months)
        """
        impact_score = self.impact_map.get(impact.lower(), 1.0)
        confidence_score = self.confidence_map.get(confidence.lower(), 50) / 100
        effort_score = self.effort_map.get(effort.lower(), 5)
        
        if effort_score == 0:
            return 0
        
        rice_score = (reach * impact_score * confidence_score) / effort_score
        return round(rice_score, 2)
    
    def prioritize_features(self, features: List[Dict]) -> List[Dict]:
        """
        Calculate RICE scores and rank features
        
        Args:
            features: List of feature dictionaries with RICE components
        """
        for feature in features:
            feature['rice_score'] = self.calculate_rice(
                feature.get('reach', 0),
                feature.get('impact', 'medium'),
                feature.get('confidence', 'medium'),
                feature.get('effort', 'm')
            )
        
        # Sort by RICE score descending
        return sorted(features, key=lambda x: x['rice_score'], reverse=True)
    
    def analyze_portfolio(self, features: List[Dict]) -> Dict:
        """
        Analyze the feature portfolio for balance and insights
        """
        if not features:
            return {}
        
        total_effort = sum(
            self.effort_map.get(f.get('effort', 'm').lower(), 5) 
            for f in features
        )
        
        total_reach = sum(f.get('reach', 0) for f in features)
        
        effort_distribution = {}
        impact_distribution = {}
        
        for feature in features:
            effort = feature.get('effort', 'm').lower()
            impact = feature.get('impact', 'medium').lower()
            
            effort_distribution[effort] = effort_distribution.get(effort, 0) + 1
            impact_distribution[impact] = impact_distribution.get(impact, 0) + 1
        
        # Calculate quick wins (high impact, low effort)
        quick_wins = [
            f for f in features 
            if f.get('impact', '').lower() in ['massive', 'high'] 
            and f.get('effort', '').lower() in ['xs', 's']
        ]
        
        # Calculate big bets (high impact, high effort)
        big_bets = [
            f for f in features 
            if f.get('impact', '').lower() in ['massive', 'high'] 
            and f.get('effort', '').lower() in ['l', 'xl']
        ]
        
        return {
            'total_features': len(features),
            'total_effort_months': total_effort,
            'total_reach': total_reach,
            'average_rice': round(sum(f['rice_score'] for f in features) / len(features), 2),
            'effort_distribution': effort_distribution,
            'impact_distribution': impact_distribution,
            'quick_wins': len(quick_wins),
            'big_bets': len(big_bets),
            'quick_wins_list': quick_wins[:3],  # Top 3 quick wins
            'big_bets_list': big_bets[:3]  # Top 3 big bets
        }
    
    def generate_roadmap(self, features: List[Dict], team_capacity: int = 10) -> List[Dict]:
        """
        Generate a quarterly roadmap based on team capacity
        
        Args:
            features: Prioritized feature list
            team_capacity: Person-months available per quarter
        """
        quarters = []
        current_quarter = {
            'quarter': 1,
            'features': [],
            'capacity_used': 0,
            'capacity_available': team_capacity
        }
        
        for feature in features:
            effort = self.effort_map.get(feature.get('effort', 'm').lower(), 5)
            
            if current_quarter['capacity_used'] + effort <= team_capacity:
                current_quarter['features'].append(feature)
                current_quarter['capacity_used'] += effort
            else:
                # Move to next quarter
                current_quarter['capacity_available'] = team_capacity - current_quarter['capacity_used']
                quarters.append(current_quarter)
                
                current_quarter = {
                    'quarter': len(quarters) + 1,
                    'features': [feature],
                    'capacity_used': effort,
                    'capacity_available': team_capacity - effort
                }
        
        if current_quarter['features']:
            current_quarter['capacity_available'] = team_capacity - current_quarter['capacity_used']
            quarters.append(current_quarter)
        
        return quarters
