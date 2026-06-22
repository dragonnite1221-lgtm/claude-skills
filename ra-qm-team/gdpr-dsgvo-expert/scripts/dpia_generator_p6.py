# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dpia_generator_base import *  # noqa: F403,E402
# fmt: off
from dpia_generator_p3 import LEGAL_BASES  # noqa: E402,E501
from dpia_generator_p4 import assess_dpia_requirement, assess_risks  # noqa: E402,E501
from dpia_generator_p5 import _csd_0  # noqa: E402,E501
# fmt: on


def _csd_1(input_data):
    """Generate DPIA report in Markdown format."""
    requirement = assess_dpia_requirement(input_data)
    risks = assess_risks(input_data)

    project = input_data.get("project_name", "Unnamed Project")
    controller = input_data.get("controller", {})
    processing = input_data.get("processing_activity", {})
    subjects = input_data.get("data_subjects", {})
    personal_data = input_data.get("personal_data", {})
    operations = input_data.get("processing_operations", {})
    recipients = input_data.get("data_recipients", {})

    legal_basis = processing.get("legal_basis", "")
    legal_info = LEGAL_BASES.get(legal_basis, {})

    report = f"""# Data Protection Impact Assessment (DPIA)

    ## Project: {project}

    | Field | Value |
    |-------|-------|
    | Version | {input_data.get('version', '1.0')} |
    | Date | {input_data.get('date', datetime.now().strftime('%Y-%m-%d'))} |
    | Controller | {controller.get('name', 'N/A')} |
    | DPO Contact | {controller.get('dpo_contact', 'N/A')} |

    ---

    ## 1. DPIA Threshold Assessment

    **Result: {requirement['recommendation']}**

    Risk Score: {requirement['risk_score']}/100

    ### Triggered Criteria

    """
    if requirement['triggered_criteria']:
        for criteria in requirement['triggered_criteria']:
            report += f"- **{criteria['description']}** ({criteria['article']})\n"
    else:
        report += "- No mandatory triggers identified\n"

    report += f"""
    ---

    ## 2. Description of Processing

    ### Purpose of Processing

    {processing.get('description', 'Not specified')}

    ### Purposes

    """
    for purpose in processing.get('purposes', ['Not specified']):
        report += f"- {purpose}\n"

    report += f"""
    ### Legal Basis

    **{legal_info.get('article', 'Not specified')}**: {legal_info.get('description', processing.get('legal_basis', 'Not specified'))}

    **Justification**: {processing.get('legal_basis_justification', 'Not provided')}

    """
    if legal_info.get('requirements'):
        report += "**Requirements to satisfy:**\n"
        for req in legal_info['requirements']:
            report += f"- {req}\n"

    report += f"""
    ---

    ## 3. Data Subjects

    | Aspect | Details |
    |--------|---------|
    | Categories | {', '.join(subjects.get('categories', ['Not specified']))} |
    | Estimated Number | {subjects.get('estimated_number', 'Not specified')} |
    | Vulnerable Groups | {'Yes - ' + subjects.get('vulnerable_groups_details', '') if subjects.get('vulnerable_groups') else 'No'} |

    ---

    ## 4. Personal Data Processed

    ### Data Categories

    """
    for category in personal_data.get('categories', ['Not specified']):
        report += f"- {category}\n"

    if personal_data.get('special_categories'):
        report += "\n### Special Category Data (Art. 9)\n\n"
        for category in personal_data['special_categories']:
            report += f"- **{category}** - Requires Art. 9(2) exception\n"

    report += f"""
    ### Data Source

    {personal_data.get('source', 'Not specified')}

    ### Retention Period

    {personal_data.get('retention_period', 'Not specified')}

    ---

    ## 5. Processing Operations

    | Operation | Details |
    |-----------|---------|
    | Collection Method | {operations.get('collection_method', 'Not specified')} |
    | Storage Location | {operations.get('storage_location', 'Not specified')} |
    | Access Controls | {operations.get('access_controls', 'Not specified')} |
    | Automated Decisions | {'Yes' if operations.get('automated_decisions') else 'No'} |
    | Profiling | {'Yes' if operations.get('profiling') else 'No'} |

    ---

    ## 6. Data Recipients

    ### Internal Recipients

    """
    for recipient in recipients.get('internal', ['Not specified']):
        report += f"- {recipient}\n"

    report += "\n### External Processors\n\n"
    for processor in recipients.get('external_processors', ['None']):
        report += f"- {processor}\n"

    if recipients.get('third_countries'):
        report += "\n### Third Country Transfers\n\n"
        report += "**Warning**: Transfers require Chapter V safeguards\n\n"
        for country in recipients['third_countries']:
            report += f"- {country}\n"

    report += """
    ---

    ## 7. Risk Assessment

    """
    _csd_0(risks)
