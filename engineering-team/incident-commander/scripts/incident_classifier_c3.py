# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin3:
    def classify_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main classification method that analyzes incident data and returns
        comprehensive response recommendations.
        
        Args:
            incident_data: Dictionary containing incident information
            
        Returns:
            Dictionary with classification results and recommendations
        """
        # Extract key information from incident data
        description = incident_data.get('description', '').lower()
        affected_users = incident_data.get('affected_users', '0%')
        business_impact = incident_data.get('business_impact', 'unknown')
        service = incident_data.get('service', 'unknown service')
        duration = incident_data.get('duration_minutes', 0)
        
        # Classify severity
        severity = self._classify_severity(description, affected_users, business_impact, duration)
        
        # Determine response teams
        response_teams = self._determine_teams(description, service)
        
        # Generate initial actions
        initial_actions = self._generate_initial_actions(severity, incident_data)
        
        # Create communication template
        communication = self._generate_communication(severity, incident_data)
        
        # Calculate response timeline
        timeline = self._generate_timeline(severity)
        
        # Determine escalation path
        escalation = self._determine_escalation(severity, business_impact)
        
        return {
            "classification": {
                "severity": severity.upper(),
                "confidence": self._calculate_confidence(description, affected_users, business_impact),
                "reasoning": self._explain_classification(severity, description, affected_users),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "response": {
                "primary_team": response_teams[0] if response_teams else "General Engineering",
                "supporting_teams": response_teams[1:] if len(response_teams) > 1 else [],
                "all_teams": response_teams,
                "response_time_minutes": self.severity_rules[severity]["response_time"] // 60
            },
            "initial_actions": initial_actions,
            "communication": communication,
            "timeline": timeline,
            "escalation": escalation,
            "incident_data": {
                "service": service,
                "description": incident_data.get('description', ''),
                "affected_users": affected_users,
                "business_impact": business_impact,
                "duration_minutes": duration
            }
        }
