---
name: "board"
description: "AgentHub /hub:board command — interact with the append-only message board (.agenthub/board/) that coordinator and subagents use to communicate. Lists channels with post counts, reads a channel's posts in chronological order with YAML frontmatter, posts a new message, or replies to a thread by post-id. Channels: dispatch (coordinator → agents task assignments), progress (agents → coordinator status), results (final summaries + merge notes). Use when: you want to inspect, post to, or thread on agent coordination messages — 'check the board', 'what did the agents report', 'post to progress', 'read the results channel'."
command: /hub:board
---

# /hub:board — Message Board

Interface for the AgentHub message board. Agents and the coordinator communicate via markdown posts organized into channels.

## Usage

```
/hub:board --list                                     # List channels
/hub:board --read dispatch                            # Read dispatch channel
/hub:board --read results                             # Read results channel
/hub:board --post --channel progress --author coordinator --message "Starting eval"
```

## What It Does

### List Channels

```bash
python {skill_path}/scripts/board_manager.py --list
```

Output:
```
Board Channels:

  dispatch        2 posts
  progress        4 posts
  results         3 posts
```

### Read Channel

```bash
python {skill_path}/scripts/board_manager.py --read {channel}
```

Displays all posts in chronological order with frontmatter metadata.

### Post Message

```bash
python {skill_path}/scripts/board_manager.py \
  --post --channel {channel} --author {author} --message "{text}"
```

### Reply to Thread

```bash
python {skill_path}/scripts/board_manager.py \
  --thread {post-id} --message "{text}" --author {author}
```

## Channels

| Channel | Purpose | Who Writes |
|---------|---------|------------|
| `dispatch` | Task assignments | Coordinator |
| `progress` | Status updates | Agents |
| `results` | Final results + merge summary | Agents + Coordinator |

## Post Format

All posts use YAML frontmatter:

```markdown
---
author: agent-1
timestamp: 2026-03-17T14:35:10Z
channel: results
sequence: 1
parent: null
---

Message content here.
```

Example result post for a content task:

```markdown
---
author: agent-2
timestamp: 2026-03-17T15:20:33Z
channel: results
sequence: 2
parent: null
---

## Result Summary

- **Approach**: Storytelling angle — open with customer pain point, build to solution
- **Word count**: 1520
- **Key sections**: Hook, Problem, Solution, Social Proof, CTA
- **Confidence**: High — follows proven AIDA framework
```

## Board Rules

- **Append-only** — never edit or delete existing posts
- **Unique filenames** — `{seq:03d}-{author}-{timestamp}.md`
- **Frontmatter required** — every post has author, timestamp, channel
