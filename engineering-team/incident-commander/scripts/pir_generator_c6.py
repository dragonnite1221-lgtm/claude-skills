# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin6:
    def _infer_why_answers(self, incident_data: Dict, timeline_data: Optional[Dict]) -> List[str]:
        """Infer potential answers to why questions from available data."""
        answers = []
        
        # Look for clues in incident description
        description = incident_data.get("description", "").lower()
        
        # Common patterns and their inferred answers
        if "database" in description and ("timeout" in description or "slow" in description):
            answers.append("Database connection pool was exhausted")
            answers.append("Connection pool configuration was insufficient for peak load")
            answers.append("Load testing didn't include realistic database scenarios")
        elif "deployment" in description or "release" in description:
            answers.append("New deployment introduced a regression")
            answers.append("Code review process missed the issue")
            answers.append("Testing environment didn't match production")
        elif "network" in description or "connectivity" in description:
            answers.append("Network infrastructure had unexpected load")
            answers.append("Network monitoring wasn't comprehensive enough")
            answers.append("Redundancy mechanisms failed simultaneously")
        else:
            # Generic answers based on common root causes
            answers.extend([
                "System couldn't handle the load/request volume",
                "Monitoring didn't detect the issue early enough",
                "Error handling mechanisms were insufficient",
                "Dependencies failed without proper circuit breakers",
                "System lacked sufficient redundancy/resilience"
            ])
        
        return answers[:5]  # Return up to 5 answers
    def _find_supporting_evidence(self, answer: str, incident_data: Dict, timeline_data: Optional[Dict]) -> List[str]:
        """Find supporting evidence for RCA answers."""
        evidence = []
        
        # Look for supporting information in incident data
        if timeline_data and "timeline" in timeline_data:
            events = timeline_data["timeline"].get("events", [])
            for event in events:
                event_message = event.get("message", "").lower()
                if any(keyword in event_message for keyword in answer.lower().split()):
                    evidence.append(f"Timeline event: {event['message']}")
        
        # Check incident metadata for supporting info
        metadata = incident_data.get("metadata", {})
        for key, value in metadata.items():
            if isinstance(value, str) and any(keyword in value.lower() for keyword in answer.lower().split()):
                evidence.append(f"Incident metadata: {key} = {value}")
        
        return evidence[:3]  # Return top 3 pieces of evidence
    def _extract_root_causes(self, whys: List[Dict]) -> List[Dict]:
        """Extract root causes from 5 Whys analysis."""
        root_causes = []
        
        # The deepest "why" answers are typically closest to root causes
        if len(whys) >= 3:
            for i, why in enumerate(whys[-2:]):  # Look at last 2 whys
                if "further investigation needed" not in why["answer"].lower():
                    root_causes.append({
                        "cause": why["answer"],
                        "category": self._categorize_root_cause(why["answer"]),
                        "evidence": why["evidence"],
                        "confidence": "high" if len(why["evidence"]) > 1 else "medium"
                    })
        
        return root_causes
    def _categorize_root_cause(self, cause: str) -> str:
        """Categorize a root cause into standard categories."""
        cause_lower = cause.lower()
        
        if any(keyword in cause_lower for keyword in ["process", "procedure", "review", "change management"]):
            return "Process"
        elif any(keyword in cause_lower for keyword in ["training", "knowledge", "skill", "experience"]):
            return "People"
        elif any(keyword in cause_lower for keyword in ["system", "architecture", "code", "configuration"]):
            return "Technology"
        elif any(keyword in cause_lower for keyword in ["network", "infrastructure", "dependency", "third-party"]):
            return "Environment"
        else:
            return "Unknown"
    def _identify_category_factors(self, category: str, incident_data: Dict, timeline_data: Optional[Dict]) -> List[Dict]:
        """Identify contributing factors for a Fishbone category."""
        factors = []
        description = incident_data.get("description", "").lower()
        
        if category == "People":
            if "misconfigured" in description or "human error" in description:
                factors.append({"factor": "Configuration error", "likelihood": "high"})
            if timeline_data and self._has_delayed_response(timeline_data):
                factors.append({"factor": "Delayed incident response", "likelihood": "medium"})
            
        elif category == "Process":
            if "deployment" in description:
                factors.append({"factor": "Insufficient deployment validation", "likelihood": "high"})
            if "code review" in incident_data.get("context", "").lower():
                factors.append({"factor": "Code review process gaps", "likelihood": "medium"})
            
        elif category == "Technology":
            if "database" in description:
                factors.append({"factor": "Database performance limitations", "likelihood": "high"})
            if "timeout" in description or "latency" in description:
                factors.append({"factor": "System performance bottlenecks", "likelihood": "high"})
            
        elif category == "Environment":
            if "network" in description:
                factors.append({"factor": "Network infrastructure issues", "likelihood": "medium"})
            if "third-party" in description or "external" in description:
                factors.append({"factor": "External service dependencies", "likelihood": "medium"})
        
        return factors
