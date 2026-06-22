# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_triage_base import *  # noqa: F403,E402


def _print_text_report(result: dict) -> None:
    """Print a human-readable triage report to stdout."""
    sep = "=" * 70
    print(sep)
    print("  INCIDENT TRIAGE REPORT")
    print(sep)
    print(f"  Timestamp     : {result.get('timestamp_utc', 'N/A')}")
    print(f"  Incident Type : {result.get('incident_type', 'unknown').upper()}")
    print(f"  Severity      : {result.get('severity', 'N/A').upper()}")
    print(f"  Confidence    : {result.get('classification_confidence', 0.0):.0%}")
    print(sep)

    fp = result.get("false_positive_indicators", [])
    if fp:
        print(f"\n  [!] FALSE POSITIVE FLAGS: {', '.join(fp)}")
        print("      Review before escalating.")

    esc_trigger = result.get("escalation_trigger_fired")
    if esc_trigger:
        print(f"\n  [!] ESCALATION TRIGGER FIRED -> {esc_trigger.upper()}")

    path = result.get("escalation_path", {})
    print(f"\n  Escalate To   : {path.get('escalate_to', 'N/A')}")
    print(f"  Response SLA  : {path.get('response_sla_minutes', 'N/A')} minutes")
    print(f"  Bridge Call   : {'YES' if path.get('bridge_call') else 'no'}")
    print(f"  War Room      : {'YES' if path.get('war_room') else 'no'}")
    print(f"  MITRE         : {path.get('mitre_technique', 'N/A')}")

    forensics = result.get("forensic_analysis", {})
    if forensics:
        print(f"\n  Forensic Fields:")
        print(f"    Source IP     : {forensics.get('source_ip', 'N/A')}")
        print(f"    User Account  : {forensics.get('user_account', 'N/A')}")
        print(f"    Hostname      : {forensics.get('hostname', 'N/A')}")
        print(f"    Process       : {forensics.get('process_name', 'N/A')}")
        print(f"    Dwell (hrs)   : {forensics.get('dwell_hours', 0.0)}")
        print(f"    Dwell Severity: {forensics.get('dwell_severity', 'N/A')}")

    ioc_summary = result.get("ioc_summary", {})
    if ioc_summary:
        print(f"\n  IOC Summary:")
        print(f"    Total IOCs    : {ioc_summary.get('total_ioc_count', 0)}")
        if ioc_summary.get("ip_indicators"):
            print(f"    IPs           : {', '.join(ioc_summary['ip_indicators'])}")
        if ioc_summary.get("hash_indicators"):
            print(f"    Hashes        : {len(ioc_summary['hash_indicators'])} hash(es)")
        print(f"    Evidence Srcs : {', '.join(ioc_summary.get('evidence_sources_applicable', []))}")

    print(f"\n  Recommended Action: {result.get('recommended_action', 'N/A')}")
    print(sep)
def _csd_0(fp_indicators, severity):
    if fp_indicators:
        recommended_action = (
            f"Verify false positive flags before escalating: {', '.join(fp_indicators)}. "
            "Confirm with asset owner and close or reclassify."
        )
    elif severity == "sev1":
        recommended_action = (
            "IMMEDIATE: Declare SEV1, open war room, page CISO and CEO. "
            "Isolate affected systems, preserve evidence, activate IR playbook."
        )
    elif severity == "sev2":
        recommended_action = (
            "URGENT: Page SOC Lead and CISO. Open bridge call. "
            "Contain impacted accounts/hosts and begin forensic collection."
        )
    elif severity == "sev3":
        recommended_action = (
            "Notify SOC Lead and Security Manager. "
            "Investigate during business hours and document findings."
        )
    else:
        recommended_action = (
            "Queue for L3 Analyst review. "
            "Document and track per standard operating procedure."
        )
    return recommended_action
