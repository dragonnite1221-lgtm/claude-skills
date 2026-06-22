# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin3:
    def _load_lessons_learned_categories(self) -> Dict[str, List[str]]:
        """Load categories for organizing lessons learned."""
        return {
            "detection_and_monitoring": [
                "Monitoring gaps identified",
                "Alert fatigue issues",
                "Detection timing improvements",
                "Observability enhancements"
            ],
            "response_and_escalation": [
                "Response time improvements",
                "Escalation path optimization",
                "Communication effectiveness",
                "Resource allocation lessons"
            ],
            "technical_systems": [
                "Architecture resilience",
                "Failure mode analysis",
                "Performance bottlenecks",
                "Dependency management"
            ],
            "process_and_procedures": [
                "Runbook effectiveness",
                "Change management gaps",
                "Review process improvements",
                "Documentation quality"
            ],
            "team_and_culture": [
                "Training needs identified",
                "Cross-team collaboration",
                "Knowledge sharing gaps",
                "Decision-making processes"
            ]
        }
    def generate_pir(self, incident_data: Dict[str, Any], timeline_data: Optional[Dict] = None,
                    rca_method: str = "five_whys", template_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate a comprehensive PIR document from incident data.
        
        Args:
            incident_data: Core incident information
            timeline_data: Optional timeline reconstruction data
            rca_method: RCA framework to use
            template_type: PIR template type (comprehensive, standard, brief)
            
        Returns:
            Dictionary containing PIR document and metadata
        """
        # Extract incident information
        incident_info = self._extract_incident_info(incident_data)
        
        # Generate root cause analysis
        rca_results = self._perform_rca(incident_data, timeline_data, rca_method)
        
        # Generate lessons learned
        lessons_learned = self._generate_lessons_learned(incident_data, timeline_data, rca_results)
        
        # Generate action items
        action_items = self._generate_action_items(incident_data, rca_results, lessons_learned)
        
        # Create timeline section
        timeline_section = self._create_timeline_section(timeline_data, incident_info["severity"])
        
        # Generate document sections
        sections = self._generate_document_sections(
            incident_info, rca_results, lessons_learned, action_items, timeline_section
        )
        
        # Build final document
        template = self.pir_templates[template_type]
        pir_document = template.format(**sections)
        
        # Generate metadata
        metadata = self._generate_metadata(incident_info, rca_results, action_items)
        
        return {
            "pir_document": pir_document,
            "metadata": metadata,
            "incident_info": incident_info,
            "rca_results": rca_results,
            "lessons_learned": lessons_learned,
            "action_items": action_items,
            "generation_timestamp": datetime.now(timezone.utc).isoformat()
        }
    def _extract_incident_info(self, incident_data: Dict) -> Dict[str, Any]:
        """Extract and normalize incident information."""
        return {
            "incident_id": incident_data.get("incident_id", "INC-" + datetime.now().strftime("%Y%m%d-%H%M")),
            "title": incident_data.get("title", incident_data.get("description", "Incident")[:50]),
            "description": incident_data.get("description", "No description provided"),
            "severity": incident_data.get("severity", "unknown").lower(),
            "start_time": self._parse_timestamp(incident_data.get("start_time", incident_data.get("timestamp", ""))),
            "end_time": self._parse_timestamp(incident_data.get("end_time", "")),
            "duration": self._calculate_duration(incident_data),
            "affected_services": incident_data.get("affected_services", []),
            "customer_impact": incident_data.get("customer_impact", "Unknown impact"),
            "business_impact": incident_data.get("business_impact", "Unknown business impact"),
            "incident_commander": incident_data.get("incident_commander", "TBD"),
            "responders": incident_data.get("responders", []),
            "status": incident_data.get("status", "resolved")
        }
