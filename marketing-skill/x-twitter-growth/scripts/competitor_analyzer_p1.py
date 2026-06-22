# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


@dataclass
class CompetitorProfile:
    handle: str
    followers: int = 0
    following: int = 0
    posts_per_week: float = 0
    avg_likes: float = 0
    avg_replies: float = 0
    avg_retweets: float = 0
    thread_frequency: str = ""  # daily, weekly, rarely
    top_topics: list = field(default_factory=list)
    content_mix: dict = field(default_factory=dict)  # format: percentage
    posting_times: list = field(default_factory=list)
    bio: str = ""
    notes: str = ""
@dataclass
class CompetitiveInsight:
    category: str
    finding: str
    opportunity: str
    priority: str  # HIGH, MEDIUM, LOW
def calculate_engagement_rate(profile: CompetitorProfile) -> float:
    if profile.followers <= 0:
        return 0
    total_engagement = profile.avg_likes + profile.avg_replies + profile.avg_retweets
    return (total_engagement / profile.followers) * 100
def analyze_competitors(competitors: list) -> list:
    insights = []

    # Engagement comparison
    engagement_rates = []
    for c in competitors:
        er = calculate_engagement_rate(c)
        engagement_rates.append((c.handle, er))

    if engagement_rates:
        top = max(engagement_rates, key=lambda x: x[1])
        if top[1] > 0:
            insights.append(CompetitiveInsight(
                "Engagement", f"Highest engagement: {top[0]} ({top[1]:.2f}%)",
                "Study their top posts — what format and topics drive replies?",
                "HIGH"
            ))

    # Posting frequency
    frequencies = [(c.handle, c.posts_per_week) for c in competitors if c.posts_per_week > 0]
    if frequencies:
        avg_freq = sum(f for _, f in frequencies) / len(frequencies)
        insights.append(CompetitiveInsight(
            "Frequency", f"Average posting: {avg_freq:.0f}/week across competitors",
            f"Match or exceed {avg_freq:.0f} posts/week to compete for mindshare",
            "HIGH"
        ))

    # Thread usage
    thread_users = [c.handle for c in competitors if c.thread_frequency in ("daily", "weekly")]
    if thread_users:
        insights.append(CompetitiveInsight(
            "Format", f"Active thread users: {', '.join(thread_users)}",
            "Threads are a proven growth lever in your niche. Publish 2-3/week minimum.",
            "HIGH"
        ))

    # Reply engagement
    reply_heavy = [(c.handle, c.avg_replies) for c in competitors if c.avg_replies > c.avg_likes * 0.3]
    if reply_heavy:
        names = [h for h, _ in reply_heavy]
        insights.append(CompetitiveInsight(
            "Community", f"High reply ratios: {', '.join(names)}",
            "These accounts build community through conversation. Ask more questions in your tweets.",
            "MEDIUM"
        ))

    # Follower/following ratio
    for c in competitors:
        if c.followers > 0 and c.following > 0:
            ratio = c.followers / c.following
            if ratio > 10:
                insights.append(CompetitiveInsight(
                    "Authority", f"{c.handle} has {ratio:.0f}x follower/following ratio",
                    "Strong authority signal — they attract followers without follow-backs",
                    "LOW"
                ))

    # Topic gaps
    all_topics = []
    for c in competitors:
        all_topics.extend(c.top_topics)

    if all_topics:
        from collections import Counter
        common = Counter(all_topics).most_common(5)
        insights.append(CompetitiveInsight(
            "Topics", f"Most covered topics: {', '.join(t for t, _ in common)}",
            "Cover these topics to compete, but find unique angles. What are they NOT covering?",
            "MEDIUM"
        ))

    return insights
