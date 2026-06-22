# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin4:
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        
        return None
    def _calculate_duration(self, incident_data: Dict) -> str:
        """Calculate incident duration in human-readable format."""
        start_time = self._parse_timestamp(incident_data.get("start_time", ""))
        end_time = self._parse_timestamp(incident_data.get("end_time", ""))
        
        if start_time and end_time:
            duration = end_time - start_time
            total_minutes = int(duration.total_seconds() / 60)
            
            if total_minutes < 60:
                return f"{total_minutes} minutes"
            elif total_minutes < 1440:  # Less than 24 hours
                hours = total_minutes // 60
                minutes = total_minutes % 60
                return f"{hours}h {minutes}m"
            else:
                days = total_minutes // 1440
                hours = (total_minutes % 1440) // 60
                return f"{days}d {hours}h"
        
        return incident_data.get("duration", "Unknown duration")
    def _perform_rca(self, incident_data: Dict, timeline_data: Optional[Dict], method: str) -> Dict[str, Any]:
        """Perform root cause analysis using specified method."""
        if method == "five_whys":
            return self._five_whys_analysis(incident_data, timeline_data)
        elif method == "fishbone":
            return self._fishbone_analysis(incident_data, timeline_data)
        elif method == "timeline":
            return self._timeline_analysis(incident_data, timeline_data)
        elif method == "bow_tie":
            return self._bow_tie_analysis(incident_data, timeline_data)
        else:
            return self._five_whys_analysis(incident_data, timeline_data)  # Default
    def _five_whys_analysis(self, incident_data: Dict, timeline_data: Optional[Dict]) -> Dict[str, Any]:
        """Perform 5 Whys root cause analysis."""
        problem_statement = incident_data.get("description", "Incident occurred")
        
        # Generate why questions based on incident data
        whys = []
        current_issue = problem_statement
        
        # Generate systematic why questions
        why_patterns = [
            f"Why did {current_issue}?",
            "Why wasn't this detected earlier?",
            "Why didn't existing safeguards prevent this?",
            "Why wasn't there a backup mechanism?",
            "Why wasn't this scenario anticipated?"
        ]
        
        # Try to infer answers from incident data
        potential_answers = self._infer_why_answers(incident_data, timeline_data)
        
        for i, why_question in enumerate(why_patterns):
            answer = potential_answers[i] if i < len(potential_answers) else "Further investigation needed"
            whys.append({
                "question": why_question,
                "answer": answer,
                "evidence": self._find_supporting_evidence(answer, incident_data, timeline_data)
            })
        
        # Identify root causes from the analysis
        root_causes = self._extract_root_causes(whys)
        
        return {
            "method": "five_whys",
            "problem_statement": problem_statement,
            "why_analysis": whys,
            "root_causes": root_causes,
            "confidence": self._calculate_rca_confidence(whys, incident_data)
        }
