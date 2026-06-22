# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


def format_json_output(result: Dict) -> str:
    """Format result as pretty JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_text_output(result: Dict) -> str:
    """Format result as human-readable text."""
    classification = result["classification"]
    response = result["response"]
    actions = result["initial_actions"]
    communication = result["communication"]
    
    output = []
    output.append("=" * 60)
    output.append("INCIDENT CLASSIFICATION REPORT")
    output.append("=" * 60)
    output.append("")
    
    # Classification section
    output.append("CLASSIFICATION:")
    output.append(f"  Severity: {classification['severity']}")
    output.append(f"  Confidence: {classification['confidence']:.1%}")
    output.append(f"  Reasoning: {classification['reasoning']}")
    output.append(f"  Timestamp: {classification['timestamp']}")
    output.append("")
    
    # Response section
    output.append("RECOMMENDED RESPONSE:")
    output.append(f"  Primary Team: {response['primary_team']}")
    if response['supporting_teams']:
        output.append(f"  Supporting Teams: {', '.join(response['supporting_teams'])}")
    output.append(f"  Response Time: {response['response_time_minutes']} minutes")
    output.append("")
    
    # Actions section
    output.append("INITIAL ACTIONS:")
    for i, action in enumerate(actions[:5], 1):  # Show first 5 actions
        output.append(f"  {i}. {action['action']} (Priority {action['priority']})")
        output.append(f"     Timeout: {action['timeout_minutes']} minutes")
        output.append(f"     {action['description']}")
        output.append("")
    
    # Communication section
    output.append("COMMUNICATION:")
    output.append(f"  Subject: {communication['subject']}")
    output.append(f"  Urgency: {communication['urgency'].upper()}")
    output.append(f"  Recipients: {', '.join(communication['recipients'])}")
    output.append(f"  Channels: {', '.join(communication['channels'])}")
    if communication['frequency_minutes'] > 0:
        output.append(f"  Update Frequency: Every {communication['frequency_minutes']} minutes")
    output.append("")
    
    output.append("=" * 60)
    
    return "\n".join(output)


def parse_input_text(text: str) -> Dict[str, Any]:
    """Parse free-form text input into structured incident data."""
    # Basic parsing - in a real system, this would be more sophisticated
    incident_data = {
        "description": text.strip(),
        "service": "unknown service",
        "affected_users": "unknown",
        "business_impact": "unknown"
    }
    
    # Try to extract service name
    service_patterns = [
        r'(?:service|api|database|server|application)\s+(\w+)',
        r'(\w+)(?:\s+(?:is|has|service|api|database))',
        r'(?:^|\s)(\w+)\s+(?:down|failed|broken)'
    ]
    
    for pattern in service_patterns:
        match = re.search(pattern, text.lower())
        if match:
            incident_data["service"] = match.group(1)
            break
    
    # Try to extract user impact
    impact_patterns = [
        r'(\d+%)\s+(?:of\s+)?(?:users?|customers?)',
        r'(?:all|every|100%)\s+(?:users?|customers?)',
        r'(?:some|many|several)\s+(?:users?|customers?)'
    ]
    
    for pattern in impact_patterns:
        match = re.search(pattern, text.lower())
        if match:
            incident_data["affected_users"] = match.group(1) if match.group(1) else match.group(0)
            break
    
    # Try to infer business impact
    if any(word in text.lower() for word in ['critical', 'urgent', 'emergency', 'down', 'outage']):
        incident_data["business_impact"] = "high"
    elif any(word in text.lower() for word in ['slow', 'degraded', 'performance']):
        incident_data["business_impact"] = "medium"
    elif any(word in text.lower() for word in ['minor', 'cosmetic', 'small']):
        incident_data["business_impact"] = "low"
    
    return incident_data
