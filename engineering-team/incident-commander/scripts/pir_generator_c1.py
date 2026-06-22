# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin1:
    def _load_pir_templates(self) -> Dict[str, str]:
        """Load PIR document templates for different severity levels."""
        return {
            "comprehensive": """# Post-Incident Review: {incident_title}

## Executive Summary
{executive_summary}

## Incident Overview
- **Incident ID:** {incident_id}
- **Date & Time:** {incident_date}
- **Duration:** {duration}
- **Severity:** {severity}
- **Status:** {status}
- **Incident Commander:** {incident_commander}
- **Responders:** {responders}

### Customer Impact
{customer_impact}

### Business Impact  
{business_impact}

## Timeline
{timeline_section}

## Root Cause Analysis
{rca_section}

## What Went Well
{what_went_well}

## What Didn't Go Well
{what_went_wrong}

## Lessons Learned
{lessons_learned}

## Action Items
{action_items}

## Follow-up and Prevention
{prevention_measures}

## Appendix
{appendix_section}

---
*Generated on {generation_date} by PIR Generator*
""",
            "standard": """# Post-Incident Review: {incident_title}

## Summary
{executive_summary}

## Incident Details
- **Date:** {incident_date}
- **Duration:** {duration}  
- **Severity:** {severity}
- **Impact:** {customer_impact}

## Timeline
{timeline_section}

## Root Cause
{rca_section}

## Action Items
{action_items}

## Lessons Learned
{lessons_learned}

---
*Generated on {generation_date}*
""",
            "brief": """# Incident Review: {incident_title}

**Date:** {incident_date} | **Duration:** {duration} | **Severity:** {severity}

## What Happened
{executive_summary}

## Root Cause
{rca_section}

## Actions
{action_items}

---
*{generation_date}*
"""
        }
