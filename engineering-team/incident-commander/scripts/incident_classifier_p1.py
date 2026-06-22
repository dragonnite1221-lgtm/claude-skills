# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402
from incident_classifier_p0 import format_text_output  # noqa: F401,E501


def interactive_mode():
    """Run in interactive mode, prompting user for input."""
    classifier = IncidentClassifier()
    
    print("🚨 Incident Classifier - Interactive Mode")
    print("=" * 50)
    print("Enter incident details (or 'quit' to exit):")
    print()
    
    while True:
        try:
            description = input("Incident description: ").strip()
            if description.lower() in ['quit', 'exit', 'q']:
                break
            
            if not description:
                print("Please provide an incident description.")
                continue
            
            service = input("Affected service (optional): ").strip() or "unknown"
            affected_users = input("Affected users (e.g., '50%', 'all users'): ").strip() or "unknown"
            business_impact = input("Business impact (high/medium/low): ").strip() or "unknown"
            
            incident_data = {
                "description": description,
                "service": service,
                "affected_users": affected_users,
                "business_impact": business_impact
            }
            
            result = classifier.classify_incident(incident_data)
            print("\n" + "=" * 50)
            print(format_text_output(result))
            print("=" * 50)
            print()
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
