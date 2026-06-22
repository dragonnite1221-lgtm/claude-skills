# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from board_manager_base import *  # noqa: F403,E402


BOARD_PATH = ".agenthub/board"
def get_board_path():
    """Get the board directory path."""
    if not os.path.isdir(BOARD_PATH):
        print(f"Error: Board not found at {BOARD_PATH}. Run hub_init.py first.",
              file=sys.stderr)
        sys.exit(1)
    return BOARD_PATH
def load_index():
    """Load the board index."""
    index_path = os.path.join(get_board_path(), "_index.json")
    if not os.path.exists(index_path):
        return {"channels": ["dispatch", "progress", "results"], "counters": {}}
    with open(index_path) as f:
        return json.load(f)
def save_index(index):
    """Save the board index."""
    index_path = os.path.join(get_board_path(), "_index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")
def list_channels(output_format="text"):
    """List all board channels with post counts."""
    index = load_index()
    channels = []
    for ch in index.get("channels", []):
        ch_path = os.path.join(get_board_path(), ch)
        count = 0
        if os.path.isdir(ch_path):
            count = len([f for f in os.listdir(ch_path)
                        if f.endswith(".md")])
        channels.append({"channel": ch, "posts": count})

    if output_format == "json":
        print(json.dumps({"channels": channels}, indent=2))
    else:
        print("Board Channels:")
        print()
        for ch in channels:
            print(f"  {ch['channel']:<15} {ch['posts']} posts")
def parse_post_frontmatter(content):
    """Parse YAML frontmatter from a post."""
    metadata = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1].strip()
            body = parts[2].strip()
            for line in fm.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip()] = val.strip()
    return metadata, body
def read_channel(channel, output_format="text"):
    """Read all posts in a channel."""
    ch_path = os.path.join(get_board_path(), channel)
    if not os.path.isdir(ch_path):
        print(f"Error: Channel '{channel}' not found", file=sys.stderr)
        sys.exit(1)

    files = sorted([f for f in os.listdir(ch_path) if f.endswith(".md")])
    posts = []

    for fname in files:
        filepath = os.path.join(ch_path, fname)
        with open(filepath) as f:
            content = f.read()
        metadata, body = parse_post_frontmatter(content)
        posts.append({
            "file": fname,
            "metadata": metadata,
            "body": body,
        })

    if output_format == "json":
        print(json.dumps({"channel": channel, "posts": posts}, indent=2))
    else:
        print(f"Channel: {channel} ({len(posts)} posts)")
        print("=" * 60)
        for post in posts:
            author = post["metadata"].get("author", "unknown")
            timestamp = post["metadata"].get("timestamp", "")
            print(f"\n--- {post['file']} (by {author}, {timestamp}) ---")
            print(post["body"])
def create_post(channel, author, message, parent=None):
    """Create a new post in a channel."""
    ch_path = os.path.join(get_board_path(), channel)
    os.makedirs(ch_path, exist_ok=True)

    # Get next sequence number
    index = load_index()
    counters = index.get("counters", {})
    seq = counters.get(channel, 0) + 1
    counters[channel] = seq
    index["counters"] = counters
    save_index(index)

    # Generate filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_author = re.sub(r"[^a-zA-Z0-9_-]", "", author)
    filename = f"{seq:03d}-{safe_author}-{timestamp}.md"

    # Build post content
    lines = [
        "---",
        f"author: {author}",
        f"timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"channel: {channel}",
        f"sequence: {seq}",
    ]
    if parent:
        lines.append(f"parent: {parent}")
    else:
        lines.append("parent: null")
    lines.append("---")
    lines.append("")
    lines.append(message)
    lines.append("")

    filepath = os.path.join(ch_path, filename)
    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print(f"Posted to {channel}/{filename}")
    return filename
