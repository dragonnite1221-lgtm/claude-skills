# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin4:
    def _classify_severity(self, description: str, affected_users: str, 
                          business_impact: str, duration: int) -> str:
        """Classify incident severity based on multiple factors."""
        scores = {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}
        
        # Keyword analysis
        for severity, rules in self.severity_rules.items():
            for keyword in rules["keywords"]:
                if keyword in description:
                    scores[severity] += 2
            
            for indicator in rules["impact_indicators"]:
                if indicator.lower() in description or indicator.lower() in affected_users.lower():
                    scores[severity] += 3
        
        # Business impact weighting
        if business_impact.lower() in ['critical', 'high', 'severe']:
            scores["sev1"] += 5
            scores["sev2"] += 3
        elif business_impact.lower() in ['medium', 'moderate']:
            scores["sev2"] += 3
            scores["sev3"] += 2
        elif business_impact.lower() in ['low', 'minimal']:
            scores["sev3"] += 2
            scores["sev4"] += 3
        
        # User impact analysis
        if '%' in affected_users:
            try:
                percentage = float(re.findall(r'\d+', affected_users)[0])
                if percentage >= 75:
                    scores["sev1"] += 4
                elif percentage >= 25:
                    scores["sev2"] += 4
                elif percentage >= 5:
                    scores["sev3"] += 3
                else:
                    scores["sev4"] += 2
            except (IndexError, ValueError):
                pass
        
        # Duration consideration
        if duration > 0:
            if duration >= 3600:  # 1 hour
                scores["sev1"] += 2
                scores["sev2"] += 1
            elif duration >= 1800:  # 30 minutes
                scores["sev2"] += 2
                scores["sev3"] += 1
        
        # Return highest scoring severity
        return max(scores, key=scores.get)
    def _determine_teams(self, description: str, service: str) -> List[str]:
        """Determine which teams should respond based on affected systems."""
        teams = set()
        text_to_analyze = f"{description} {service}".lower()
        
        for component, team_list in self.team_mappings.items():
            if component in text_to_analyze:
                teams.update(team_list)
        
        # Default teams if no specific match
        if not teams:
            teams = {"General Engineering", "SRE"}
        
        return list(teams)
    def _generate_initial_actions(self, severity: str, incident_data: Dict) -> List[Dict]:
        """Generate prioritized initial actions based on severity."""
        base_actions = self.action_templates[severity].copy()
        
        # Customize actions based on incident details
        for action in base_actions:
            if severity in ["sev1", "sev2"]:
                action["urgency"] = "immediate" if severity == "sev1" else "high"
            else:
                action["urgency"] = "normal" if severity == "sev3" else "low"
        
        return base_actions
    def _generate_communication(self, severity: str, incident_data: Dict) -> Dict:
        """Generate communication template filled with incident data."""
        template = self.communication_templates[severity]
        
        # Fill template with incident data
        now = datetime.now(timezone.utc)
        service = incident_data.get('service', 'Unknown Service')
        description = incident_data.get('description', 'Incident detected')
        
        communication = {
            "subject": template["subject"].format(
                service=service,
                brief_description=description[:50] + "..." if len(description) > 50 else description
            ),
            "body": template["body"],
            "urgency": severity,
            "recipients": self._determine_recipients(severity),
            "channels": self._determine_channels(severity),
            "frequency_minutes": self._get_update_frequency(severity)
        }
        
        return communication
