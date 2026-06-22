# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from customer_interview_analyzer_base import *  # noqa: F403,E402


def aggregate_interviews(interviews: List[Dict]) -> Dict:
    """Aggregate insights from multiple interviews"""
    aggregated = {
        'total_interviews': len(interviews),
        'common_pain_points': defaultdict(list),
        'common_requests': defaultdict(list),
        'jobs_to_be_done': [],
        'overall_sentiment': {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        },
        'top_themes': Counter(),
        'metrics_summary': set(),
        'competitors_mentioned': Counter()
    }
    
    for interview in interviews:
        # Aggregate pain points
        for pain in interview.get('pain_points', []):
            indicator = pain.get('indicator', 'unknown')
            aggregated['common_pain_points'][indicator].append(pain['quote'])
        
        # Aggregate requests
        for request in interview.get('feature_requests', []):
            req_type = request.get('type', 'general')
            aggregated['common_requests'][req_type].append(request['quote'])
        
        # Aggregate JTBD
        aggregated['jobs_to_be_done'].extend(interview.get('jobs_to_be_done', []))
        
        # Aggregate sentiment
        sentiment = interview.get('sentiment_score', {}).get('label', 'neutral')
        aggregated['overall_sentiment'][sentiment] += 1
        
        # Aggregate themes
        for theme in interview.get('key_themes', []):
            aggregated['top_themes'][theme] += 1
        
        # Aggregate metrics
        aggregated['metrics_summary'].update(interview.get('metrics_mentioned', []))
        
        # Aggregate competitors
        for competitor in interview.get('competitors_mentioned', []):
            aggregated['competitors_mentioned'][competitor] += 1
    
    # Process aggregated data
    aggregated['common_pain_points'] = dict(aggregated['common_pain_points'])
    aggregated['common_requests'] = dict(aggregated['common_requests'])
    aggregated['top_themes'] = dict(aggregated['top_themes'].most_common(10))
    aggregated['metrics_summary'] = list(aggregated['metrics_summary'])
    aggregated['competitors_mentioned'] = dict(aggregated['competitors_mentioned'])
    
    return aggregated


def format_single_interview(analysis: Dict) -> str:
    """Format single interview analysis"""
    output = ["=" * 60]
    output.append("CUSTOMER INTERVIEW ANALYSIS")
    output.append("=" * 60)
    
    # Sentiment
    sentiment = analysis['sentiment_score']
    output.append(f"\n📊 Overall Sentiment: {sentiment['label'].upper()}")
    output.append(f"   Score: {sentiment['score']}")
    output.append(f"   Positive signals: {sentiment['positive_signals']}")
    output.append(f"   Negative signals: {sentiment['negative_signals']}")
    
    # Pain Points
    if analysis['pain_points']:
        output.append("\n🔥 Pain Points Identified:")
        for i, pain in enumerate(analysis['pain_points'][:5], 1):
            output.append(f"\n{i}. [{pain['severity'].upper()}] {pain['quote'][:100]}...")
    
    # Feature Requests
    if analysis['feature_requests']:
        output.append("\n💡 Feature Requests:")
        for i, req in enumerate(analysis['feature_requests'][:5], 1):
            output.append(f"\n{i}. [{req['type']}] Priority: {req['priority']}")
            output.append(f"   \"{req['quote'][:100]}...\"")
    
    # Jobs to Be Done
    if analysis['jobs_to_be_done']:
        output.append("\n🎯 Jobs to Be Done:")
        for i, job in enumerate(analysis['jobs_to_be_done'], 1):
            output.append(f"{i}. {job['job']}")
    
    # Key Themes
    if analysis['key_themes']:
        output.append("\n🏷️ Key Themes:")
        output.append(", ".join(analysis['key_themes']))
    
    # Key Quotes
    if analysis['quotes']:
        output.append("\n💬 Key Quotes:")
        for i, quote in enumerate(analysis['quotes'][:3], 1):
            output.append(f'{i}. "{quote}"')
    
    # Metrics
    if analysis['metrics_mentioned']:
        output.append("\n📈 Metrics Mentioned:")
        output.append(", ".join(analysis['metrics_mentioned']))
    
    # Competitors
    if analysis['competitors_mentioned']:
        output.append("\n🏢 Competitors Mentioned:")
        output.append(", ".join(analysis['competitors_mentioned']))
    
    return "\n".join(output)
