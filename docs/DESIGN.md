# Design language

The interface should feel like a trusted, warm colleague: calm enough for serious work, human enough that a journalist or auditor wants to open it. It is not a dashboard of alarms.

## Concept: kanga-inspired
Kanga cloth is everyday Kenyan and East African design: bold repeating motifs, confident colour, often paired with a saying. The interface borrows that:
- a **repeating motif strip** across the top of the page (diamonds, rings and dots)
- **concentric-ring motif** in the hero card
- a **Swahili proverb** in the footer: *Kuuliza si ujinga* ("asking is not ignorance"), because every flag is a question for a person to ask
- friendly microcopy such as *Habari* ("hello") and *Here is what deserves a second look today*

## Colour
| Role | Hex | Use |
|---|---|---|
| Aubergine | `#3b1147` | Headings, selected states, hero |
| Plum | `#5e2373` | Buttons, tier 1 |
| Rose | `#e4577f` | Accent, headline highlight, chart gradient |
| Apricot / Gold | `#f7a65a` / `#f0be4d` | Motif, sparkline |
| Teal | `#1e8c82` / `#dff4f0` | Innocent explanations and "ok" states |
| Blush | `#fff8f4` | Page background |

Deliberately **no alarm red** on anything that names an entity. Tiers use plum, rose and apricot tints so they read as priority, not guilt. The teal "possible innocent explanations" tags are always visible.

## Type
- **Fraunces** (soft serif) for headings and numbers: warm and editorial
- **DM Sans** for interface text: clear at small sizes
Both are bundled under the SIL Open Font License (`src/uwazi/ui/fonts/`), so the app looks the same everywhere and works offline.

## Accessibility
Contrast ratios (WCAG 2.x, computed from the palette):
| Pair | Ratio | Result |
|---|---|---|
| Body ink on blush | 15.9 | AA/AAA |
| Muted text on white | 4.9 | AA |
| White on aubergine | 15.5 | AA/AAA |
| Tier 1 / 2 / 3 chips | 8.6 / 4.8 / 5.0 | AA |
| Teal tag text | 5.5 | AA |
| Rose accent on blush | 3.4 | Large text only (30 px headline), passes the 3:1 large-text rule |

Meaning never relies on colour alone: tiers are labelled in text, and every chart marker has a text value. The layout is responsive (the hero motif shrinks on phones so it never sits under text).
Planned: screen-reader audit, keyboard flow review of the award dialog, Swahili strings.

## Tone
Plain language. Say "unusual compared with similar purchases", not "suspicious". Say "worth a second look", not "risky". Show what we cannot see before what we found.

## Changing the look
All styling lives in `src/uwazi/ui/theme.py` (colours are CSS variables at the top) and `src/uwazi/ui/components.py` (HTML blocks).
