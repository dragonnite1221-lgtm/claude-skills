---
title: "Epic Design Skill — Agent Skill & Codex Plugin"
description: "Build immersive, cinematic 2.5D interactive websites using scroll storytelling, parallax depth, text animations, and premium scroll effects with CSS. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Epic Design Skill

<div class="page-meta" markdown>
<span class="meta-badge">:material-code-braces: Engineering - Core</span>
<span class="meta-badge">:material-identifier: `epic-design`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-skills</code>
</div>


Build cinematic, immersive websites that feel premium and alive using only flat PNG/static
assets, CSS, and JavaScript (GSAP). No WebGL or 3D software. Every page gets depth layers that
respond to scroll, intentional text entrances/exits, and cinematic section transitions.

**Before starting:** if `project-context.md` or `product-context.md` exists, read it first and
only ask for what it doesn't cover.

## Modes

- **Build from scratch** — assets + brief in hand. Run the full workflow (Steps 1–5).
- **Enhance existing site** — skip to Step 2, analyze current structure, recommend depth
  assignments and animation opportunities.
- **Debug/fix** — run `validate-layers.js`, check GPU rules, verify reduced-motion handling.

## Step 1 — Brief + Asset Inspection

Before writing code: extract the brief (product/content, mood, section count), then inspect
**every** image the user provides.

```bash
# Requires Pillow (pip install Pillow). Reports format, background status, and depth hints.
python3 scripts/inspect-assets.py path/to/image.png
python3 scripts/inspect-assets.py path/to/assets/   # whole directory
```

For each asset: confirm format (JPEG has no real alpha), read the background status
(clean cutout / solid dark / solid light / complex scene), then **judge whether the background
actually needs removing** — remove it for isolated products, floating characters, and logos;
**keep** it for screenshots, full-bleed backgrounds, artwork, device mockups, and any depth-0
background. Never auto-remove. Report every asset's status to the user and state your depth
assignments before building. Full judgment rules, notification format, and resize targets:
[asset-pipeline.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/asset-pipeline.md).

**Compositional hierarchy** (before any code): one asset is the HERO (50–80vw, depth-3);
companions are 15–25% of the hero's size (depth-2, hugging its edges); accents are tiny
(1–5vw, depth-5); background fills the section (depth-0). When the hero exits on scroll,
companions scatter outward rather than just fading.

## Step 2 — Choose Techniques

Match user intent to a technique combo, then read the full implementation from `references/`.

| User says | Primary pattern | Text technique | Special effect |
|-----------|----------------|----------------|----------------|
| Product launch / brand site | Inter-section floating product + perspective zoom | Split converge + word lighting | DJI scale-in pin |
| Hero with big title | 6-layer parallax + pinned sticky | Offset diagonal + masked line reveal | Bleed typography |
| Cinematic sections | Curtain panel roll-up + scrub timeline | Theatrical enter+exit | Top-down clip birth |
| Apple-style animation | Scrub timeline + clip-path wipe | Word-by-word scroll lighting | Character cylinder |
| Elements between sections | Floating product + clip-path birth | Scramble text | Window pane iris |
| Cards / features | Cascading card stack | Skew + elastic bounce | Section peel |
| Portfolio / showcase | Horizontal scroll + flip morph | Line clip wipe | Diagonal wipe |
| SaaS / startup | Window pane iris + stagger grid | Variable font wave | Curved path travel |

By scroll behavior: "stays in place while things change" → `pin: true` + scrub; "rises from
section" → floating product + clip-path birth; "born from top" → top-down clip birth or curtain
roll-up; "overlap/stack" → card stack or section peel; "text flies in from sides" → split
converge; "lights up word by word" → word-by-word lighting; "section drops down" → clip-path
`inset(0 0 100% 0)` → `inset(0)`; "travels between sections" → GSAP Flip or curved path.

## Step 3 — Assign Depth to Every Element (non-negotiable)

```
DEPTH 0 → Far background   | parallax 0.10x | blur 8px | scale 0.70
DEPTH 1 → Glow/atmosphere  | parallax 0.25x | blur 4px | scale 0.85
DEPTH 2 → Mid decorations  | parallax 0.50x | blur 0px | scale 1.00
DEPTH 3 → Main objects     | parallax 0.80x | blur 0px | scale 1.05
DEPTH 4 → UI / text        | parallax 1.00x | blur 0px | scale 1.00
DEPTH 5 → Foreground FX    | parallax 1.20x | blur 0px | scale 1.10
```

Apply as `data-depth="3"` on the element + matching `.depth-3` CSS class. Full model:
[depth-system.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/depth-system.md).

## Step 4 — Accessibility & Performance (mandatory in every output)

- Ship a `@media (prefers-reduced-motion: reduce)` block that drops animation/transition
  durations to `0.01ms` and disables smooth scroll.
- Only animate `transform`, `opacity`, `filter`, `clip-path` — never `width/height/top/left`.
- `will-change: transform` only on actively animating elements; remove it after.
- `content-visibility: auto` on off-screen sections; `IntersectionObserver` to animate only
  in-viewport elements; reduce effects on touch via `matchMedia('(pointer: coarse)')`.

Details: [performance.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/performance.md), [accessibility.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/accessibility.md).

## Step 5 — Code Structure & Output

Every section is a `.scene` wrapper containing **3+ depth layers**, hero image at depth-3, text
at depth-4, decorative layers `aria-hidden="true"`:

```html
<section class="scene" data-scene="hero" style="--scene-height: 200vh">
  <div class="layer depth-0" data-depth="0" aria-hidden="true"><!-- bg gradient/texture --></div>
  <div class="layer depth-1" data-depth="1" aria-hidden="true"><!-- glow/atmosphere --></div>
  <div class="layer depth-2" data-depth="2" aria-hidden="true"><!-- mid decorations --></div>
  <div class="layer depth-3" data-depth="3">
    <img class="product-hero float-loop" src="product.png" alt="[description]" />
  </div>
  <div class="layer depth-4" data-depth="4">
    <h1 class="split-text" data-animate="converge">Your Headline</h1>
  </div>
  <div class="layer depth-5" data-depth="5" aria-hidden="true"><!-- foreground FX --></div>
</section>
```

Deliver a **single self-contained HTML file** (inline CSS+JS unless separate files are asked),
GSAP via jsDelivr CDN (`gsap@3.12.5`), commented sections, and a top-of-file note listing which
of the 45 techniques were applied.

## Step 6 — Validate

```bash
node scripts/validate-layers.js path/to/index.html
```

Checks depth attributes, `aria-hidden` on decorative layers, reduced-motion CSS, image alt text,
SplitText `aria-label`, the 80-animated-element ceiling, and that `will-change` isn't global.
Fix any reported failure and re-run until it passes.

## Quick Rules (non-negotiable)

1. Always inspect assets and judge backgrounds before coding; state depth assignments first.
2. Every section ≥ 3 depth layers; every text element ≥ 1 animation technique.
3. Every project includes a `prefers-reduced-motion` fallback.
4. Only animate GPU-safe properties; product images default to depth-3, backgrounds to depth-0 (slight blur).
5. Floating loop (6–14s) on any hero element; decorative elements get `aria-hidden="true"`.
6. Reduce effects on mobile (`pointer: coarse`); remove `will-change` after animations complete.

## Proactive Triggers

Surface without being asked: JPEG product images can't be transparent (offer the inspector);
all assets the same size (flag hierarchy, recommend hero+companion sizing); no depth assignments
mentioned; "smooth animations" requested without reduced-motion handling; parallax without GPU
optimization; more than 80 animated elements (recommend reducing or lazy-loading).

## Reference Files

| File | What's inside |
|------|--------------|
| [asset-pipeline.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/asset-pipeline.md) | Asset inspection, bg-judgment rules, notification format, CSS knockout, resize targets |
| [depth-system.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/depth-system.md) | 6-layer depth model, CSS/JS, blur/scale formulas |
| [motion-system.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/motion-system.md) | 9 scroll architecture patterns with full GSAP code |
| [text-animations.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/text-animations.md) | 13 text techniques with implementation code |
| [directional-reveals.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/directional-reveals.md) | 8 clip-path "born from top/sides" techniques |
| [inter-section-effects.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/inter-section-effects.md) | Floating product, GSAP Flip, cross-section travel |
| [performance.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/performance.md) | GPU rules, will-change, IntersectionObserver patterns |
| [accessibility.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/accessibility.md) | WCAG 2.1 AA, prefers-reduced-motion, ARIA |
| [examples.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/epic-design/references/examples.md) | 5 complete real-world implementations |

## Related Skills

- **senior-frontend** — the full app around the 2.5D site (not the cinematic effects).
- **ui-design** — visual layout and components (not scroll animations/depth).
- **landing-page-generator** — quick SaaS landing scaffolds (not custom cinematic experiences).
- **page-cro** — conversion optimization after the build.
- **accessibility-auditor** — full WCAG verification (this skill ships basic reduced-motion handling).
