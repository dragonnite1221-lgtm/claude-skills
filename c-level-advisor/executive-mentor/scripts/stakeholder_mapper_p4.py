# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from stakeholder_mapper_base import *  # noqa: F403,E402
# fmt: off
from stakeholder_mapper_p2 import hr  # noqa: E402,E501
from stakeholder_mapper_p3 import print_report  # noqa: E402,E501
# fmt: on


def interactive_mode():
    print()
    print(hr("═"))
    print("  STAKEHOLDER MAPPER — Interactive Mode")
    print(hr("═"))
    
    data = {}
    data["initiative"] = input("\nWhat initiative or decision are you mapping?\n> ").strip()
    
    print("\nAdd stakeholders one at a time. Empty name to finish.")
    print("Scores: 1=low, 10=high")
    print()
    
    stakeholders = []
    while True:
        name = input(f"Stakeholder {len(stakeholders)+1} name (or ENTER to finish): ").strip()
        if not name:
            if len(stakeholders) < 1:
                print("  Need at least 1 stakeholder.")
                continue
            break
        
        role = input(f"  Role/title: ").strip()
        
        def get_score(prompt, default=5):
            while True:
                s = input(f"  {prompt} (1–10, default {default}): ").strip()
                if not s:
                    return float(default)
                try:
                    v = float(s)
                    if 1 <= v <= 10:
                        return v
                    print("  Must be 1–10")
                except ValueError:
                    print("  Enter a number")
        
        influence = get_score("Influence (power over this decision)")
        alignment = get_score("Alignment (1=opposed, 10=champion)")
        interest = get_score("Interest level (how engaged are they)")
        notes = input(f"  Notes (optional): ").strip()
        
        stakeholders.append({
            "name": name,
            "role": role,
            "influence": influence,
            "alignment": alignment,
            "interest": interest,
            "notes": notes
        })
        print()
    
    data["stakeholders"] = stakeholders
    print_report(data)
SAMPLE_DATA = {
    "initiative": "Migrate from monolith to microservices (18-month program)",
    "stakeholders": [
        {
            "name": "Sarah Chen (CTO)",
            "role": "Chief Technology Officer",
            "influence": 10,
            "alignment": 9,
            "interest": 9,
            "notes": "Driving force behind the initiative. Will fund and protect the team."
        },
        {
            "name": "Marcus Webb (CFO)",
            "role": "Chief Financial Officer",
            "influence": 9,
            "alignment": 3,
            "interest": 6,
            "notes": "Concerned about 18-month cost with no visible revenue return. Has budget veto."
        },
        {
            "name": "Priya Agarwal (VP Eng)",
            "role": "VP Engineering",
            "influence": 8,
            "alignment": 7,
            "interest": 8,
            "notes": "Supportive in principle, worried about team bandwidth alongside feature delivery."
        },
        {
            "name": "Tom Briggs (VP Product)",
            "role": "VP Product",
            "influence": 7,
            "alignment": 4,
            "interest": 5,
            "notes": "Concerned about roadmap slowdown. Hasn't been in the architecture discussions."
        },
        {
            "name": "Elena Park (CEO)",
            "role": "Chief Executive Officer",
            "influence": 10,
            "alignment": 6,
            "interest": 4,
            "notes": "Trusts the CTO but will back out if CFO and VP Product both push back hard."
        },
        {
            "name": "Raj Patel (Lead Arch)",
            "role": "Lead Architect",
            "influence": 6,
            "alignment": 10,
            "interest": 10,
            "notes": "Deep technical champion. Has proposed detailed migration plan."
        },
        {
            "name": "Dev Team Leads (x4)",
            "role": "Team Leads",
            "influence": 5,
            "alignment": 6,
            "interest": 7,
            "notes": "Mixed. Some excited, some worried about learning curve. Middle ground."
        },
        {
            "name": "Board (investor reps)",
            "role": "Board Directors",
            "influence": 9,
            "alignment": 5,
            "interest": 3,
            "notes": "Not paying attention unless CFO raises flags. Could become blockers if CFO escalates."
        }
    ]
}
