# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from topic_cluster_mapper_base import *  # noqa: F403,E402


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "how", "what", "why", "when", "where", "who", "which", "that", "this",
    "it", "its", "do", "does", "your", "our", "my", "their", "we", "you",
    "get", "make", "use", "using", "used", "can", "will", "should", "best",
}
def simple_stem(word: str) -> str:
    """Very simple suffix-stripping stemmer."""
    w = word.lower()
    if len(w) <= 3:
        return w
    # Order matters — try longer suffixes first
    suffixes = [
        "ization", "isation", "ational", "fulness", "ousness", "iveness",
        "iveness", "ingness", "ations", "nesses", "ators", "ation",
        "ating", "alism", "ality", "alize", "alise", "ation", "ator",
        "ness", "ment", "less", "tion", "sion", "tion", "ing", "ers",
        "ies", "ied", "ily", "ful", "ous", "ive", "ize", "ise", "est",
        "ed", "er", "ly", "al", "ic", "s",
    ]
    for sfx in suffixes:
        if w.endswith(sfx) and len(w) - len(sfx) >= 3:
            return w[: -len(sfx)]
    return w
def extract_stems(topic: str) -> set:
    words = re.findall(r"\b[a-zA-Z]+\b", topic.lower())
    return {simple_stem(w) for w in words if w not in STOP_WORDS and len(w) > 2}
def compute_similarity(stems_a: set, stems_b: set) -> float:
    """Jaccard similarity between two stem sets."""
    if not stems_a or not stems_b:
        return 0.0
    intersection = stems_a & stems_b
    union = stems_a | stems_b
    return len(intersection) / len(union)
def build_clusters(topics: list, threshold: float = 0.15) -> list:
    """
    Greedy clustering: assign each topic to the first cluster it's
    similar-enough to; else start a new cluster.
    """
    # Pre-compute stems
    topic_stems = {t: extract_stems(t) for t in topics}

    clusters = []  # list of {"pillar": str, "topics": [str], "stems": set}

    for topic in topics:
        t_stems = topic_stems[topic]
        best_cluster = None
        best_score = 0.0

        for cluster in clusters:
            sim = compute_similarity(t_stems, cluster["stems"])
            if sim > best_score:
                best_score = sim
                best_cluster = cluster

        if best_cluster and best_score >= threshold:
            best_cluster["topics"].append(topic)
            best_cluster["stems"] |= t_stems  # grow cluster centroid
        else:
            clusters.append({
                "pillar": topic,
                "topics": [topic],
                "stems": set(t_stems),
            })

    # Identify best pillar: topic with most shared stems to others in cluster
    for cluster in clusters:
        if len(cluster["topics"]) == 1:
            continue
        all_stems = [topic_stems[t] for t in cluster["topics"]]
        best_topic = cluster["topics"][0]
        best_conn = 0
        for i, topic in enumerate(cluster["topics"]):
            conn = sum(
                len(topic_stems[topic] & topic_stems[other])
                for j, other in enumerate(cluster["topics"]) if i != j
            )
            if conn > best_conn:
                best_conn = conn
                best_topic = topic
        cluster["pillar"] = best_topic

    return clusters
def _make_recommendations(clusters: list) -> list:
    recs = []
    large = [c for c in clusters if c["size"] >= 3]
    singletons = [c for c in clusters if c["size"] == 1]

    if large:
        recs.append(f"Create {len(large)} pillar page(s) for clusters with 3+ topics")
    if singletons:
        recs.append(
            f"{len(singletons)} singleton topic(s) — consider merging or expanding to form mini-clusters"
        )
    if clusters:
        biggest = clusters[0]
        recs.append(
            f"Highest-priority cluster: '{biggest['pillar_topic']}' "
            f"({biggest['size']} related topics) — start content here"
        )
    return recs
def build_output(topics: list, clusters: list) -> dict:
    cluster_output = []
    for i, c in enumerate(clusters, 1):
        supporting = [t for t in c["topics"] if t != c["pillar"]]
        cluster_output.append({
            "cluster_id": i,
            "pillar_topic": c["pillar"],
            "size": len(c["topics"]),
            "supporting_topics": supporting,
            "suggested_url_slug": re.sub(r"[^a-z0-9]+", "-", c["pillar"].lower()).strip("-"),
        })

    # Sort by cluster size desc
    cluster_output.sort(key=lambda x: -x["size"])

    return {
        "total_topics": len(topics),
        "total_clusters": len(clusters),
        "clusters": cluster_output,
        "recommendations": _make_recommendations(cluster_output),
    }
