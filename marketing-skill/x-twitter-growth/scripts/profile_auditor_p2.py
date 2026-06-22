# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from profile_auditor_base import *  # noqa: F403,E402
# fmt: off
from profile_auditor_p1 import AuditFinding, ProfileData  # noqa: E402,E501
# fmt: on


def audit_activity(profile: ProfileData) -> list:
    findings = []

    # Posting frequency
    if profile.posts_per_week <= 0:
        findings.append(AuditFinding("Activity", "CRITICAL", "No posting data provided",
                                     "Provide --posts-per-week estimate"))
    elif profile.posts_per_week < 3:
        findings.append(AuditFinding("Activity", "CRITICAL",
                                     f"Very low posting ({profile.posts_per_week:.0f}/week)",
                                     "Minimum 7 posts/week (1/day). Aim for 14-21."))
    elif profile.posts_per_week < 7:
        findings.append(AuditFinding("Activity", "WARN",
                                     f"Low posting ({profile.posts_per_week:.0f}/week)",
                                     "Aim for 2-3 posts per day for consistent growth"))
    elif profile.posts_per_week < 21:
        findings.append(AuditFinding("Activity", "GOOD",
                                     f"Good posting cadence ({profile.posts_per_week:.0f}/week)"))
    else:
        findings.append(AuditFinding("Activity", "GOOD",
                                     f"High posting cadence ({profile.posts_per_week:.0f}/week)"))

    # Reply ratio
    if profile.reply_ratio > 0:
        if profile.reply_ratio < 0.2:
            findings.append(AuditFinding("Activity", "WARN",
                                         f"Low reply ratio ({profile.reply_ratio:.0%})",
                                         "Aim for 30%+ replies. Engage with others, don't just broadcast."))
        elif profile.reply_ratio >= 0.3:
            findings.append(AuditFinding("Activity", "GOOD",
                                         f"Healthy reply ratio ({profile.reply_ratio:.0%})"))

    # Follower/following ratio
    if profile.followers > 0 and profile.following > 0:
        ratio = profile.followers / profile.following
        if ratio < 0.5:
            findings.append(AuditFinding("Profile", "WARN",
                                         f"Low follower/following ratio ({ratio:.1f}x)",
                                         "Unfollow inactive accounts. Ratio should trend toward 2:1+"))
        elif ratio >= 2:
            findings.append(AuditFinding("Profile", "GOOD",
                                         f"Healthy follower/following ratio ({ratio:.1f}x)"))

    # Pinned tweet
    if profile.has_pinned:
        if profile.pinned_age_days > 30:
            findings.append(AuditFinding("Profile", "WARN",
                                         f"Pinned tweet is {profile.pinned_age_days} days old",
                                         "Update pinned tweet monthly with your latest best content"))
        else:
            findings.append(AuditFinding("Profile", "GOOD", "Pinned tweet is recent"))
    else:
        findings.append(AuditFinding("Profile", "WARN", "No pinned tweet",
                                     "Pin your best-performing tweet or thread. It's your landing page."))

    return findings
def calculate_score(findings: list) -> tuple:
    total = len(findings)
    if total == 0:
        return 0, "F"

    good = sum(1 for f in findings if f.status == "GOOD")
    score = int((good / total) * 100)

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    return score, grade
def generate_recommendations(findings: list, profile: ProfileData) -> list:
    recs = []
    criticals = [f for f in findings if f.status == "CRITICAL"]
    warns = [f for f in findings if f.status == "WARN"]

    for f in criticals:
        if f.fix:
            recs.append(f"🔴 {f.fix}")

    for f in warns[:3]:  # Top 3 warnings
        if f.fix:
            recs.append(f"🟡 {f.fix}")

    # Stage-specific advice
    if profile.followers < 1000:
        recs.append("📈 Growth phase: Focus 70% on replies to larger accounts, 30% on your own posts")
    elif profile.followers < 10000:
        recs.append("📈 Momentum phase: 2-3 threads/week + daily engagement. Start a recurring series.")
    else:
        recs.append("📈 Scale phase: Leverage audience with cross-platform repurposing + newsletter growth")

    return recs
