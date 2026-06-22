# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


def format_json_output(result: Dict) -> str:
    """Format result as pretty JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_markdown_output(result: Dict) -> str:
    """Format result as Markdown PIR document."""
    return result.get("pir_document", "Error: No PIR document generated")


def format_text_output(result: Dict) -> str:
    """Format result as human-readable summary."""
    if "error" in result:
        return f"Error: {result['error']}"
    
    metadata = result.get("metadata", {})
    incident_info = result.get("incident_info", {})
    rca_results = result.get("rca_results", {})
    action_items = result.get("action_items", [])
    
    output = []
    output.append("=" * 60)
    output.append("POST-INCIDENT REVIEW SUMMARY")  
    output.append("=" * 60)
    output.append("")
    
    # Basic info
    output.append("INCIDENT INFORMATION:")
    output.append(f"  PIR ID: {metadata.get('pir_id', 'Unknown')}")
    output.append(f"  Severity: {incident_info.get('severity', 'Unknown').upper()}")
    output.append(f"  Duration: {incident_info.get('duration', 'Unknown')}")
    output.append(f"  Status: {incident_info.get('status', 'Unknown').title()}")
    output.append("")
    
    # RCA summary
    output.append("ROOT CAUSE ANALYSIS:")
    output.append(f"  Method: {rca_results.get('method', 'Unknown')}")
    output.append(f"  Confidence: {rca_results.get('confidence', 'Unknown').title()}")
    
    root_causes = rca_results.get("root_causes", [])
    if root_causes:
        output.append(f"  Root Causes Identified: {len(root_causes)}")
        for i, cause in enumerate(root_causes[:3], 1):
            output.append(f"    {i}. {cause.get('cause', 'Unknown')[:60]}...")
    output.append("")
    
    # Action items summary
    output.append("ACTION ITEMS:")
    output.append(f"  Total Actions: {len(action_items)}")
    output.append(f"  Critical (P0): {metadata.get('critical_action_items', 0)}")
    output.append(f"  Prevention Timeline: {metadata.get('estimated_prevention_timeline', 'Unknown')}")
    
    if action_items:
        output.append("  Top Actions:")
        for item in action_items[:3]:
            output.append(f"    - {item.get('title', 'Unknown')[:50]}...")
    output.append("")
    
    # Completeness
    completeness = metadata.get("review_completeness", 0) * 100
    output.append(f"REVIEW COMPLETENESS: {completeness:.0f}%")
    output.append("")
    
    output.append("=" * 60)
    
    return "\n".join(output)
