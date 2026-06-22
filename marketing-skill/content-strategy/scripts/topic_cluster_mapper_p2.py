# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from topic_cluster_mapper_base import *  # noqa: F403,E402
# fmt: off
from topic_cluster_mapper_p1 import build_clusters, build_output  # noqa: E402,E501
# fmt: on


DEMO_TOPICS = [
    "email marketing strategy",
    "email subject line tips",
    "email open rate optimization",
    "email automation workflows",
    "SEO keyword research",
    "on-page SEO optimization",
    "SEO content strategy",
    "technical SEO audit",
    "social media marketing",
    "social media content calendar",
    "Instagram marketing tips",
    "LinkedIn marketing for B2B",
    "content marketing ROI",
    "content strategy planning",
    "blog content ideas",
    "landing page conversion rate",
    "conversion rate optimization",
    "A/B testing landing pages",
    "paid ads budget allocation",
    "Google Ads campaign setup",
]
def main():
    parser = argparse.ArgumentParser(
        description="Topic cluster mapper — groups keywords into content clusters."
    )
    parser.add_argument("--file", help="Text file with one topic/keyword per line")
    parser.add_argument("--threshold", type=float, default=0.15,
                        help="Similarity threshold for clustering (default: 0.15)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
    else:
        topics = DEMO_TOPICS
        if not args.json:
            print("No input provided — running in demo mode with 20 marketing topics.\n")

    if not topics:
        print("No topics found.", file=sys.stderr)
        sys.exit(1)

    clusters = build_clusters(topics, threshold=args.threshold)
    output = build_output(topics, clusters)

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("=" * 62)
    print(f"  TOPIC CLUSTER MAP   {output['total_topics']} topics → {output['total_clusters']} clusters")
    print("=" * 62)

    for cluster in output["clusters"]:
        print(f"\n  Cluster {cluster['cluster_id']}  ({cluster['size']} topics)")
        print(f"  ┌─ PILLAR: {cluster['pillar_topic']}")
        print(f"  │  Slug:   /{cluster['suggested_url_slug']}")
        for st in cluster["supporting_topics"]:
            print(f"  └─ Supporting: {st}")

    print("\n" + "=" * 62)
    print("  RECOMMENDATIONS")
    print("=" * 62)
    for rec in output["recommendations"]:
        print(f"  • {rec}")
    print()
