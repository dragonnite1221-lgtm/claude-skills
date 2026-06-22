# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from profile_auditor_base import *  # noqa: F403,E402


@dataclass
class ProfileData:
    handle: str = ""
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts_per_week: float = 0
    reply_ratio: float = 0  # % of posts that are replies
    thread_ratio: float = 0  # % of posts that are threads
    has_pinned: bool = False
    pinned_age_days: int = 0
    has_link: bool = False
    has_newsletter: bool = False
    avg_engagement_rate: float = 0  # likes+replies+rts / followers
@dataclass
class AuditFinding:
    area: str
    status: str  # GOOD, WARN, CRITICAL
    message: str
    fix: str = ""
@dataclass
class AuditReport:
    handle: str
    score: int = 0
    max_score: int = 100
    grade: str = ""
    findings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
def audit_bio(profile: ProfileData) -> list:
    findings = []
    bio = profile.bio.strip()

    if not bio:
        findings.append(AuditFinding("Bio", "CRITICAL", "No bio provided for audit",
                                     "Provide bio text with --bio flag"))
        return findings

    # Length check
    if len(bio) < 30:
        findings.append(AuditFinding("Bio", "WARN", f"Bio too short ({len(bio)} chars)",
                                     "Aim for 100-160 characters with clear value prop"))
    elif len(bio) > 160:
        findings.append(AuditFinding("Bio", "WARN", f"Bio may be too long ({len(bio)} chars)",
                                     "Keep under 160 chars for readability"))
    else:
        findings.append(AuditFinding("Bio", "GOOD", f"Bio length OK ({len(bio)} chars)"))

    # Hashtag check
    hashtags = re.findall(r'#\w+', bio)
    if hashtags:
        findings.append(AuditFinding("Bio", "WARN", f"Hashtags in bio ({', '.join(hashtags)})",
                                     "Remove hashtags — signals amateur. Use plain text."))
    else:
        findings.append(AuditFinding("Bio", "GOOD", "No hashtags in bio"))

    # Buzzword check
    buzzwords = ['entrepreneur', 'guru', 'ninja', 'rockstar', 'visionary', 'hustler',
                 'thought leader', 'serial entrepreneur', 'dreamer', 'doer']
    found = [bw for bw in buzzwords if bw.lower() in bio.lower()]
    if found:
        findings.append(AuditFinding("Bio", "WARN", f"Buzzwords detected: {', '.join(found)}",
                                     "Replace with specific, concrete descriptions of what you do"))

    # Specificity check — pipes and slashes often signal unfocused bios
    if bio.count('|') >= 3 or bio.count('/') >= 3:
        findings.append(AuditFinding("Bio", "WARN", "Bio may lack focus (too many roles/identities)",
                                     "Lead with ONE clear identity. What's the #1 thing you want to be known for?"))

    # Social proof check
    proof_patterns = [r'\d+[kKmM]?\+?\s*(followers|subscribers|readers|users|customers)',
                      r'(founder|ceo|cto|vp|head|director|lead)\s+(of|at|@)',
                      r'(author|writer)\s+of', r'featured\s+in', r'ex-\w+']
    has_proof = any(re.search(p, bio, re.IGNORECASE) for p in proof_patterns)
    if has_proof:
        findings.append(AuditFinding("Bio", "GOOD", "Social proof detected"))
    else:
        findings.append(AuditFinding("Bio", "WARN", "No obvious social proof in bio",
                                     "Add a credential: title, metric, brand association, or achievement"))

    # CTA/Link check
    if profile.has_link:
        findings.append(AuditFinding("Bio", "GOOD", "Profile has a link"))
    else:
        findings.append(AuditFinding("Bio", "WARN", "No link in profile",
                                     "Add a link to newsletter, product, or portfolio"))

    return findings
