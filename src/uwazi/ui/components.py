"""HTML building blocks. All dynamic text is escaped. Strings contain no blank lines so Streamlit renders them as raw HTML."""
from __future__ import annotations

import html
from datetime import date

import pandas as pd

from ..indicators import INDICATORS

E = lambda s: html.escape(str(s))  # noqa: E731
ICONS = {
    "car": '<path d="M5 17h14M3 13l2-6h14l2 6v4H3zM7 17v2M17 17v2"/>',
    "laptop": '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 20h20"/>',
    "road": '<path d="M8 3L4 21M16 3l4 18M12 5v3M12 11v3M12 17v3"/>',
    "pencil": '<path d="M4 20l1-4L16 5l3 3L8 19z"/>',
    "doc": '<path d="M7 3h7l4 4v14H7zM14 3v5h5M10 13h5M10 17h5"/>',
}
PALETTE = ["#c23566", "#1e8c82", "#d9931a", "#7a3b8f"]


def money_short(n: float) -> str:
    return f"{n/1e9:.1f}bn" if n >= 1e9 else f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}K" if n >= 1e3 else f"{n:.0f}"


def _icon_key(category: str) -> str:
    c = category.lower()
    return "car" if "vehicle" in c else "laptop" if ("laptop" in c or "computer" in c) else "road" if ("road" in c or "works" in c) else "pencil" if "station" in c else "doc"


def svg(path: str, size: int = 24) -> str:
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>')


def color_index(category: str) -> int:
    return sum(map(ord, category)) % 4


def kanga_strip() -> str:
    return '<div class="kanga"></div>'


def brand(note: str = "Synthetic demo data") -> str:
    lens = ('<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#ffe9b0" stroke-width="2" stroke-linecap="round">'
            '<circle cx="11" cy="11" r="6"/><path d="M16 16l4.5 4.5"/><circle cx="11" cy="11" r="1.7" fill="#f0be4d" stroke="none"/></svg>')
    return (f'<div class="brand"><span class="logo">{lens}</span><div><h1>Uwazi Trace</h1><p>Public funds, in plain sight</p></div>'
            f'<span class="pillnote">{E(note)}</span></div>')


def chip(tier: int) -> str:
    return f'<span class="chip t{tier}">Tier {tier}</span>'


def alert_row(a, outcome: str | None = None) -> str:
    n = len(a.indicators)
    status = f" · {E(outcome.replace('_', ' '))}" if outcome else ""
    return (f'<div class="row"><span class="ico i{color_index(a.category)}">{svg(ICONS[_icon_key(a.category)])}</span>'
            f'<div class="rm"><b>{E(a.category)}</b><small>{E(a.entity)} · {E(a.supplier)}</small>'
            f'<small>{n} {"signal" if n == 1 else "signals"}{status}</small></div>'
            f'<div class="rr"><b>KES {money_short(a.award_value_kes)}</b>{chip(a.tier)}</div></div>')


def sparkline(values: list[float]) -> str:
    if len(values) < 2:
        return ""
    w, h, top = 320, 92, max(values) or 1
    pts = [(i / (len(values) - 1) * w, h - 8 - v / top * (h - 26)) for i, v in enumerate(values)]
    line = "".join(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true"><defs>'
            '<linearGradient id="sg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#f0be4d" stop-opacity=".5"/>'
            '<stop offset="1" stop-color="#f0be4d" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{line}L{w} {h}L0 {h}Z" fill="url(#sg)"/><path d="{line}" fill="none" stroke="#f0be4d" stroke-width="2.4" '
            'vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>')


def hero(total: float, n_awards: int, unknown_bidders: float, tiers: dict, monthly: list[float]) -> str:
    stones = "".join(f'<div class="stone"><b>{tiers.get(t, 0)}</b><span>Tier {t}</span></div>' for t in (1, 2, 3))
    return (f'<div class="hero"><small>Public funds in view</small><div class="big"><span>KES</span>{total/1e9:.1f} bn</div>'
            f'<div class="sub">{n_awards:,} awards observed · {unknown_bidders:.0%} without a bidder count</div>'
            f'<div class="stones">{stones}</div>{sparkline(monthly)}</div>')


def donut(parts: list[tuple[str, float]]) -> str:
    total = sum(v for _, v in parts) or 1
    offset, circles, legend = 25.0, [], []
    for i, (label, v) in enumerate(parts):
        pct, color = v / total * 100, PALETTE[i % 4]
        circles.append(f'<circle cx="18" cy="18" r="15.9155" fill="none" stroke="{color}" stroke-width="4.6" '
                       f'stroke-dasharray="{max(pct - .7, 0):.2f} {100 - max(pct - .7, 0):.2f}" stroke-dashoffset="{offset:.2f}"/>')
        offset -= pct
        legend.append(f'<div><i style="background:{color}"></i>{E(label)}<b>{pct:.0f}%</b></div>')
    return (f'<div class="donut"><svg viewBox="0 0 36 36" role="img" aria-label="Share of value by category">'
            f'<circle cx="18" cy="18" r="15.9155" fill="none" stroke="#f6ebf0" stroke-width="4.6"/>{"".join(circles)}</svg>'
            f'<div class="leg">{"".join(legend)}</div></div>')


def bar(label: str, sub: str, value: float, median: float | None = None, p90: float | None = None, text: str | None = None) -> str:
    marks = ""
    if median is not None and pd.notna(median):
        marks += f'<span class="mk" style="left:{median*100:.1f}%" title="peer median"></span>'
    if p90 is not None and pd.notna(p90):
        marks += f'<span class="mk" style="left:{p90*100:.1f}%;opacity:.3" title="peer 90th percentile"></span>'
    return (f'<div class="bar"><span class="lab">{E(label)}<small>{E(sub)}</small></span><span class="track">'
            f'<span class="fill" style="width:{min(max(value, 0), 1)*100:.1f}%"></span>{marks}</span><b>{E(text or f"{value:.0%}")}</b></div>')


def histogram(counts: list[int], highlight: range) -> str:
    top = max(counts + [1])
    bars = "".join(f'<i class="{"th" if i in highlight else ""}" style="height:{c/top*100:.0f}%" title="{c} awards"></i>' for i, c in enumerate(counts))
    return f'<div class="hist">{bars}</div>'


def tags(items) -> str:
    return "".join(f'<span class="tag">{E(x)}</span>' for x in items)


def finding_card(code: str, detail: str, baseline: str) -> str:
    ind = INDICATORS[code]
    return (f'<div class="card"><h3>{E(ind.name)}<span class="fam">{E(ind.family)}</span></h3>'
            f'<div class="lbl">1 · Risk indicator</div><div>{E(ind.question)}</div>'
            f'<div class="lbl">2 · Supporting data</div><div>{E(detail)}</div>'
            f'<div class="lbl">3 · Comparison and baseline</div><div>{E(baseline)}</div>'
            f'<div class="lbl">5 · Possible legitimate explanations</div><div>{tags(ind.legitimate)}</div></div>')


def award_summary(a) -> str:
    when = a.award_date.strftime("%d %b %Y") if pd.notna(a.award_date) else "date unknown"
    return (f'<div class="sum"><small>{E(a.category)} · {E(a.award_id)}</small><div class="big">KES {a.award_value_kes:,.0f}</div>'
            f'<div>{E(a.entity)} · {E(a.supplier)}</div><small>{E(a.method)} · awarded {when}</small><div style="margin-top:10px">{chip(a.tier)} '
            f'<small>{a.families} independent kinds of signal</small></div></div>')


def timeline_html(entries: list[dict]) -> str:
    items = []
    for e in entries:
        outcome, code, note = (e["detail"].split("|") + ["", ""])[:3]
        items.append(f'<div class="ev"><b>{E(e["obj"])}</b> · {E(outcome.replace("_", " "))}'
                     f'<div class="mono">{E(code or "no code")} · {E(note)} · {E(e["actor"])}</div>'
                     f'<div class="mono">{E(e["ts"][:19].replace("T", " "))} UTC · hash {E(e["hash"][:12])}</div></div>')
    return f'<div class="tl">{"".join(items)}</div>'


def proverb() -> str:
    return ('<div class="proverb">Kuuliza si ujinga.<small>“Asking is not ignorance.” A Swahili proverb, and the spirit of this tool: '
            'every flag is a question for a person to ask, never an answer.</small></div>'
            f'<div class="fine">Uwazi Trace prototype · synthetic data · {date.today().year}</div>')
