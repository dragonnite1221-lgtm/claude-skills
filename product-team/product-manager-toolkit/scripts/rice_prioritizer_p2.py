# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rice_prioritizer_base import *  # noqa: F403,E402
# fmt: off
from rice_prioritizer_p1 import RICECalculator  # noqa: E402,E501
# fmt: on


def format_output(features: List[Dict], analysis: Dict, roadmap: List[Dict]) -> str:
    """Format the results for display"""
    output = ["=" * 60]
    output.append("RICE PRIORITIZATION RESULTS")
    output.append("=" * 60)
    
    # Top prioritized features
    output.append("\n📊 TOP PRIORITIZED FEATURES\n")
    for i, feature in enumerate(features[:10], 1):
        output.append(f"{i}. {feature.get('name', 'Unnamed')}")
        output.append(f"   RICE Score: {feature['rice_score']}")
        output.append(f"   Reach: {feature.get('reach', 0)} | Impact: {feature.get('impact', 'medium')} | "
                     f"Confidence: {feature.get('confidence', 'medium')} | Effort: {feature.get('effort', 'm')}")
        output.append("")
    
    # Portfolio analysis
    output.append("\n📈 PORTFOLIO ANALYSIS\n")
    output.append(f"Total Features: {analysis.get('total_features', 0)}")
    output.append(f"Total Effort: {analysis.get('total_effort_months', 0)} person-months")
    output.append(f"Total Reach: {analysis.get('total_reach', 0):,} users")
    output.append(f"Average RICE Score: {analysis.get('average_rice', 0)}")
    
    output.append(f"\n🎯 Quick Wins: {analysis.get('quick_wins', 0)} features")
    for qw in analysis.get('quick_wins_list', []):
        output.append(f"   • {qw.get('name', 'Unnamed')} (RICE: {qw['rice_score']})")
    
    output.append(f"\n🚀 Big Bets: {analysis.get('big_bets', 0)} features")
    for bb in analysis.get('big_bets_list', []):
        output.append(f"   • {bb.get('name', 'Unnamed')} (RICE: {bb['rice_score']})")
    
    # Roadmap
    output.append("\n\n📅 SUGGESTED ROADMAP\n")
    for quarter in roadmap:
        output.append(f"\nQ{quarter['quarter']} - Capacity: {quarter['capacity_used']}/{quarter['capacity_used'] + quarter['capacity_available']} person-months")
        for feature in quarter['features']:
            output.append(f"   • {feature.get('name', 'Unnamed')} (RICE: {feature['rice_score']})")
    
    return "\n".join(output)
def load_features_from_csv(filepath: str) -> List[Dict]:
    """Load features from CSV file"""
    features = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feature = {
                'name': row.get('name', ''),
                'reach': int(row.get('reach', 0)),
                'impact': row.get('impact', 'medium'),
                'confidence': row.get('confidence', 'medium'),
                'effort': row.get('effort', 'm'),
                'description': row.get('description', '')
            }
            features.append(feature)
    return features
def create_sample_csv(filepath: str):
    """Create a sample CSV file for testing"""
    sample_features = [
        ['name', 'reach', 'impact', 'confidence', 'effort', 'description'],
        ['User Dashboard Redesign', '5000', 'high', 'high', 'l', 'Complete redesign of user dashboard'],
        ['Mobile Push Notifications', '10000', 'massive', 'medium', 'm', 'Add push notification support'],
        ['Dark Mode', '8000', 'medium', 'high', 's', 'Implement dark mode theme'],
        ['API Rate Limiting', '2000', 'low', 'high', 'xs', 'Add rate limiting to API'],
        ['Social Login', '12000', 'high', 'medium', 'm', 'Add Google/Facebook login'],
        ['Export to PDF', '3000', 'medium', 'low', 's', 'Export reports as PDF'],
        ['Team Collaboration', '4000', 'massive', 'low', 'xl', 'Real-time collaboration features'],
        ['Search Improvements', '15000', 'high', 'high', 'm', 'Enhance search functionality'],
        ['Onboarding Flow', '20000', 'massive', 'high', 's', 'Improve new user onboarding'],
        ['Analytics Dashboard', '6000', 'high', 'medium', 'l', 'Advanced analytics for users'],
    ]
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_features)
    
    print(f"Sample CSV created at: {filepath}")
def main():
    parser = argparse.ArgumentParser(description='RICE Framework for Feature Prioritization')
    parser.add_argument('input', nargs='?', help='CSV file with features or "sample" to create sample')
    parser.add_argument('--capacity', type=int, default=10, help='Team capacity per quarter (person-months)')
    parser.add_argument('--output', choices=['text', 'json', 'csv'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    # Create sample if requested
    if args.input == 'sample':
        create_sample_csv('sample_features.csv')
        return
    
    # Use sample data if no input provided
    if not args.input:
        features = [
            {'name': 'User Dashboard', 'reach': 5000, 'impact': 'high', 'confidence': 'high', 'effort': 'l'},
            {'name': 'Push Notifications', 'reach': 10000, 'impact': 'massive', 'confidence': 'medium', 'effort': 'm'},
            {'name': 'Dark Mode', 'reach': 8000, 'impact': 'medium', 'confidence': 'high', 'effort': 's'},
            {'name': 'API Rate Limiting', 'reach': 2000, 'impact': 'low', 'confidence': 'high', 'effort': 'xs'},
            {'name': 'Social Login', 'reach': 12000, 'impact': 'high', 'confidence': 'medium', 'effort': 'm'},
        ]
    else:
        features = load_features_from_csv(args.input)
    
    # Calculate RICE scores
    calculator = RICECalculator()
    prioritized = calculator.prioritize_features(features)
    analysis = calculator.analyze_portfolio(prioritized)
    roadmap = calculator.generate_roadmap(prioritized, args.capacity)
    
    # Output results
    if args.output == 'json':
        result = {
            'features': prioritized,
            'analysis': analysis,
            'roadmap': roadmap
        }
        print(json.dumps(result, indent=2))
    elif args.output == 'csv':
        # Output prioritized features as CSV
        if prioritized:
            keys = prioritized[0].keys()
            print(','.join(keys))
            for feature in prioritized:
                print(','.join(str(feature.get(k, '')) for k in keys))
    else:
        print(format_output(prioritized, analysis, roadmap))
