---
title: "Apple HIG Expert — Agent Skill for Product Teams"
description: "Design and audit apps against Apple's Human Interface Guidelines (HIG) for iOS, macOS, watchOS, and visionOS, with the 2026 Liquid Glass aesthetic. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Apple HIG Expert

<div class="page-meta" markdown>
<span class="meta-badge">:material-lightbulb-outline: Product</span>
<span class="meta-badge">:material-identifier: `apple-hig-expert`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install product-skills</code>
</div>


Design and audit apps that feel natively integrated into the Apple ecosystem while
applying the **Liquid Glass** aesthetic. Acts as a Senior Apple Design Lead: navigation,
visual styling, and accessibility against the Human Interface Guidelines.

## Before Starting

If `product-context.md` or `ios-design-context.md` exists, read it before asking questions.
Otherwise gather: (1) **platform target** — iOS / macOS / watchOS / visionOS; (2) **current
state** — new project or auditing an existing mockup/code; (3) **app category** — utility,
productivity, game, social, etc.

## Two Modes

- **Design from scratch** — focus on atomic design, layout primitives, and navigation
  paradigms aligned with Apple's core philosophies (Clarity, Deference, Depth).
- **HIG audit** — review mockups or code with [templates/hig-audit-template.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/templates/hig-audit-template.md)
  to systematically flag violations and refinement opportunities, producing a 0-100 scorecard.

## Core Principles (2026)

**Liquid Glass aesthetic** — translucency and fluid motion:
- **Translucency**: use materials (ultra-thin / thin / thick) to create hierarchy.
- **Depth**: layers reflect z-axis relationships.
- **Fluidity**: interactions feel like physical objects responding to touch/gaze.

**Accessibility first** — design for everyone from day 1:
- **VoiceOver**: every element has a semantic description.
- **Tap targets**: minimum 44x44 points for all interactive elements.
- **Contrast**: legible text against translucent backgrounds (WCAG ratios).

## Workflow

1. **Navigation & layout** — choose the right pattern (sidebars for macOS, tab bars for iOS,
   ornaments for visionOS). See [references/platform-specifics.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/references/platform-specifics.md).
2. **Visual styling** — apply San Francisco typography and semantic colors. See
   [references/visual-design.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/references/visual-design.md).
3. **Accessibility & final audit** — verify contrast, tap targets, and VoiceOver semantics
   with `hig_checker.py` (below). See [references/accessibility.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/references/accessibility.md).

## hig_checker.py

Three subcommands automate the quantitative checks:

```bash
# Contrast ratio of foreground vs background hex (WCAG pass/fail)
python scripts/hig_checker.py contrast "#FFFFFF" "#1C1C1E"

# Tap-target size in points (fails below 44x44)
python scripts/hig_checker.py target 32 32

# Batch-check a JSON file of elements (each item: {"fg": "#...", "bg": "#..."})
python scripts/hig_checker.py batch elements.json
```

## Proactive Triggers

Surface these WITHOUT being asked:
- **Low contrast** — translucent layers masking text legibility.
- **Tiny targets** — interactive elements smaller than 44pt.
- **Missing semantics** — icon buttons with no accessibility labels.
- **Density overload** — layouts that ignore white space / deference.

## Output Artifacts

| When you ask for... | You get... |
|---------------------|------------|
| "Audit my iOS app" | HIG scorecard (0-100) with prioritized fixes. |
| "Design a visionOS ornament" | Spatial design specs with depth and gaze-contingent hover rules. |
| "Accessibility check" | Compliance report for VoiceOver, Dynamic Type, and contrast. |

Output is structured: bottom line first (compliance status), then What + Why + How per
finding, with confidence tags (🟢 verified / 🟡 medium / 🔴 assumed).

## References

- [references/visual-design.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/references/visual-design.md) — Liquid Glass materials, San Francisco typography, semantic colors
- [references/platform-specifics.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/references/platform-specifics.md) — per-platform navigation, ergonomics, hardware constraints
- [references/accessibility.md](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/apple-hig-expert/references/accessibility.md) — VoiceOver, Dynamic Type, contrast standards

## Related Skills

- **ui-design-system** — token-based components (not platform HIG rules).
- **ux-researcher-designer** — persona validation (not visual styling).
- **landing-page-generator** — web marketing pages.
