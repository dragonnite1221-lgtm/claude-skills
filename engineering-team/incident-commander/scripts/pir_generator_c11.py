# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin11:
    def _generate_document_sections(self, incident_info: Dict, rca_results: Dict, 
                                  lessons_learned: Dict, action_items: List[Dict], 
                                  timeline_section: str) -> Dict[str, str]:
        """Generate all document sections for PIR template."""
        sections = {}
        
        # Basic information
        sections["incident_title"] = incident_info["title"]
        sections["incident_id"] = incident_info["incident_id"]
        sections["incident_date"] = incident_info["start_time"].strftime("%Y-%m-%d %H:%M:%S UTC") if incident_info["start_time"] else "Unknown"
        sections["duration"] = incident_info["duration"]
        sections["severity"] = incident_info["severity"].upper()
        sections["status"] = incident_info["status"].title()
        sections["incident_commander"] = incident_info["incident_commander"]
        sections["responders"] = ", ".join(incident_info["responders"]) if incident_info["responders"] else "TBD"
        sections["generation_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Impact sections
        sections["customer_impact"] = incident_info["customer_impact"]
        sections["business_impact"] = incident_info["business_impact"]
        
        # Executive summary
        sections["executive_summary"] = self._create_executive_summary(incident_info, rca_results)
        
        # Timeline
        sections["timeline_section"] = timeline_section
        
        # RCA section
        sections["rca_section"] = self._create_rca_section(rca_results)
        
        # What went well/wrong
        sections["what_went_well"] = self._create_what_went_well_section(incident_info, rca_results)
        sections["what_went_wrong"] = self._create_what_went_wrong_section(rca_results, lessons_learned)
        
        # Lessons learned
        sections["lessons_learned"] = self._create_lessons_learned_section(lessons_learned)
        
        # Action items
        sections["action_items"] = self._create_action_items_section(action_items)
        
        # Prevention and appendix
        sections["prevention_measures"] = self._create_prevention_section(rca_results, action_items)
        sections["appendix_section"] = self._create_appendix_section(incident_info)
        
        return sections
    def _create_executive_summary(self, incident_info: Dict, rca_results: Dict) -> str:
        """Create executive summary section."""
        summary_parts = []
        
        # Incident description
        summary_parts.append(f"On {incident_info['start_time'].strftime('%B %d, %Y') if incident_info['start_time'] else 'an unknown date'}, we experienced a {incident_info['severity']} incident affecting {incident_info.get('affected_services', ['our services'])}.")
        
        # Duration and impact
        summary_parts.append(f"The incident lasted {incident_info['duration']} and had the following impact: {incident_info['customer_impact']}")
        
        # Root cause summary
        root_causes = rca_results.get("root_causes", [])
        if root_causes:
            primary_cause = root_causes[0]["cause"]
            summary_parts.append(f"Root cause analysis identified the primary issue as: {primary_cause}")
        
        # Resolution
        summary_parts.append(f"The incident has been {incident_info['status']} and we have identified specific actions to prevent recurrence.")
        
        return " ".join(summary_parts)
    def _create_rca_section(self, rca_results: Dict) -> str:
        """Create RCA section content."""
        rca_content = []
        
        method = rca_results.get("method", "unknown")
        rca_content.append(f"### Analysis Method: {self.rca_frameworks.get(method, {}).get('name', method)}")
        rca_content.append("")
        
        if method == "five_whys" and "why_analysis" in rca_results:
            rca_content.append("#### Why Analysis")
            rca_content.append("")
            
            for i, why in enumerate(rca_results["why_analysis"], 1):
                rca_content.append(f"**Why {i}:** {why['question']}")
                rca_content.append(f"**Answer:** {why['answer']}")
                if why["evidence"]:
                    rca_content.append(f"**Evidence:** {', '.join(why['evidence'])}")
                rca_content.append("")
        
        elif method == "fishbone" and "categories" in rca_results:
            rca_content.append("#### Contributing Factor Analysis")
            rca_content.append("")
            
            for category, data in rca_results["categories"].items():
                if data["factors"]:
                    rca_content.append(f"**{category}:**")
                    for factor in data["factors"]:
                        rca_content.append(f"- {factor['factor']} (likelihood: {factor.get('likelihood', 'unknown')})")
                    rca_content.append("")
        
        # Root causes summary
        root_causes = rca_results.get("root_causes", [])
        if root_causes:
            rca_content.append("#### Identified Root Causes")
            rca_content.append("")
            
            for i, cause in enumerate(root_causes, 1):
                rca_content.append(f"{i}. **{cause['cause']}**")
                rca_content.append(f"   - Category: {cause.get('category', 'Unknown')}")
                rca_content.append(f"   - Confidence: {cause.get('confidence', 'Unknown')}")
                if cause.get("evidence"):
                    rca_content.append(f"   - Evidence: {cause['evidence']}")
                rca_content.append("")
        
        return "\n".join(rca_content)
