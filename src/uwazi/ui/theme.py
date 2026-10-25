"""Visual identity: a kanga-inspired palette (aubergine, rose, apricot, gold), warm serif headings,
bundled open-licence fonts (Fraunces, DM Sans) so the app looks the same everywhere, offline."""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

FONT_DIR = Path(__file__).parent / "fonts"
FACES = [("Fraunces", 600, "fraunces-latin-600-normal.woff2"), ("Fraunces", 700, "fraunces-latin-700-normal.woff2"),
         ("DM Sans", 400, "dm-sans-latin-400-normal.woff2"), ("DM Sans", 500, "dm-sans-latin-500-normal.woff2"),
         ("DM Sans", 700, "dm-sans-latin-700-normal.woff2")]

_KANGA = ('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="16" viewBox="0 0 64 16"><rect width="64" height="16" fill="#3b1147"/>'
          '<polygon points="8,2 14,8 8,14 2,8" fill="#f0be4d"/><circle cx="24" cy="8" r="4.5" fill="#e4577f"/><circle cx="24" cy="8" r="1.7" fill="#fff6f2"/>'
          '<polygon points="40,2 46,8 40,14 34,8" fill="#f7a65a"/><circle cx="56" cy="8" r="4.5" fill="none" stroke="#f0be4d" stroke-width="2"/>'
          '<circle cx="56" cy="8" r="1.4" fill="#e4577f"/></svg>')
_MOTIF = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><g fill="none" stroke-width="7"><circle cx="100" cy="100" r="90" stroke="#f0be4d"/>'
          '<circle cx="100" cy="100" r="70" stroke="#e4577f"/><circle cx="100" cy="100" r="50" stroke="#f7a65a"/><circle cx="100" cy="100" r="30" stroke="#fff6f2"/></g>'
          '<circle cx="100" cy="100" r="12" fill="#f0be4d"/></svg>')


def _uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@lru_cache(maxsize=1)
def font_face_css() -> str:
    css = []
    for family, weight, name in FACES:
        data = base64.b64encode((FONT_DIR / name).read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;font-display:swap;"
                   f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "".join(css)


CSS = """
:root{--plum:#3b1147;--plum2:#5e2373;--rose:#e4577f;--coral:#f2705f;--apricot:#f7a65a;--gold:#f0be4d;--blush:#fff8f4;--lilac:#f4eaf8;
--ink:#2a1630;--mute:#7c6a84;--line:#f1e3eb;--teal:#1e8c82;--tealsoft:#dff4f0;--card:#fff}
html,body,.stApp,[class*="css"]{font-family:'DM Sans',system-ui,sans-serif;color:var(--ink)}
.stApp{background:radial-gradient(900px 420px at 92% -8%,#fbdfe9 0,transparent 62%),radial-gradient(700px 380px at -5% 6%,#f3e4fa 0,transparent 60%),#fff8f4}
#MainMenu,footer,[data-testid="stDecoration"],.stDeployButton,[data-testid="stToolbar"]{display:none !important}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1080px;padding:3.4rem 1.25rem 4rem}
h1,h2,h3,h4{font-family:'Fraunces',Georgia,serif !important;letter-spacing:-.01em;color:var(--plum)}
.kanga{position:fixed;top:0;left:0;right:0;height:12px;z-index:999990;background:url("__KANGA__") repeat-x;background-size:auto 12px}
.brand{display:flex;align-items:center;gap:14px;margin:4px 0 4px}
.logo{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,var(--plum),var(--rose));box-shadow:0 8px 20px rgba(228,87,127,.35)}
.brand h1{font-size:28px;margin:0;line-height:1.05;padding:0}.brand p{margin:0;color:var(--mute);font-size:14px}
.pillnote{margin-left:auto;background:#fff1d6;color:#8a5a00;font-weight:700;font-size:12.5px;padding:6px 13px;border-radius:99px;white-space:nowrap}
[role="tablist"],.stTabs [data-baseweb="tab-list"]{gap:4px;background:#fff;padding:5px;border-radius:999px;width:fit-content;max-width:100%;box-shadow:0 8px 24px rgba(59,17,71,.08);margin:14px 0 10px;overflow-x:auto;border:none !important}
[role="tab"],.stTabs button[data-baseweb="tab"]{border-radius:999px !important;padding:8px 20px;height:auto;background:transparent;cursor:pointer;border:none}
[role="tab"] p{font-weight:700;color:var(--mute);font-size:14.5px;margin:0}
[role="tab"][aria-selected="true"]{background:var(--plum)}
[role="tab"][aria-selected="true"] p{color:#fff}
.react-aria-SelectionIndicator,[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none !important}
[data-testid="stTabs"]>div:first-child{border-bottom:none !important}
[class*="st-key-card_"]{background:var(--card);border-radius:24px;box-shadow:0 1px 2px rgba(59,17,71,.05),0 16px 36px rgba(59,17,71,.08);padding:20px 22px 10px;margin:14px 0}
.hd{font:600 20px/1.2 'Fraunces',serif;color:var(--plum)}.hd+.sub{color:var(--mute);font-size:13.5px;margin:4px 0 8px}
.row{border-bottom:1px solid var(--line)}
.hello{font:600 30px/1.15 'Fraunces',serif;color:var(--plum);margin:16px 2px 4px}.hello em{color:var(--rose);font-style:normal}
.lead{color:var(--mute);margin:0 2px 16px;max-width:62ch}
.card{background:var(--card);border-radius:24px;box-shadow:0 1px 2px rgba(59,17,71,.05),0 16px 36px rgba(59,17,71,.08);padding:20px 22px;margin:14px 0}
.card h3{font-size:20px;margin:0 0 4px}.card .sub{color:var(--mute);font-size:13.5px;margin:0 0 10px}
.hero{position:relative;overflow:hidden;border-radius:32px;padding:26px 28px 0;color:#fff;background:linear-gradient(135deg,#3b1147 0%,#5e2373 52%,#b23a68 120%);box-shadow:0 24px 54px rgba(59,17,71,.30);margin-top:6px}
.hero:before{content:"";position:absolute;right:-46px;top:-46px;width:280px;height:280px;background:url("__MOTIF__") no-repeat center/contain;opacity:.5}
.hero small{position:relative;opacity:.85;font-weight:600;font-size:14px}
.big{position:relative;font:700 54px/1.05 'Fraunces',serif;margin:6px 0 4px}.big span{font:700 22px 'DM Sans';opacity:.8;margin-right:6px}
.hero .sub{position:relative;opacity:.85;font-size:14px}
.stones{position:relative;display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 0}
.stone{background:rgba(255,255,255,.15);border-radius:20px;padding:10px 18px;backdrop-filter:blur(4px)}
.stone b{display:block;font:700 26px/1.1 'Fraunces',serif}.stone span{font-size:12.5px;opacity:.88}
.spark{display:block;width:calc(100% + 56px);margin:6px -28px 0;height:92px}
.row{display:flex;align-items:center;gap:14px;padding:12px 4px}
.ico{width:48px;height:48px;border-radius:17px;display:grid;place-items:center;flex:none}
.i0{background:#fde3ec;color:#c23566}.i1{background:#dff4f0;color:#126b63}.i2{background:#fff0d1;color:#a8680c}.i3{background:#efe2f6;color:#5e2373}
.rm{flex:1;min-width:0}.rm b{display:block;font-weight:700}.rm small{display:block;color:var(--mute);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rr{text-align:right;flex:none}.rr b{display:block;font-weight:700}
.chip{display:inline-block;font-size:12px;font-weight:700;padding:3px 11px;border-radius:99px;margin-top:3px}
.t1{background:#efe2f6;color:#5e2373}.t2{background:#ffe3ec;color:#b8325f}.t3{background:#fff0d9;color:#97580f}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:8px 0}
.mini{background:#fff;border-radius:22px;padding:16px;box-shadow:0 12px 28px rgba(59,17,71,.07)}
.mini b{display:block;font:700 30px/1.1 'Fraunces',serif;color:var(--plum)}.mini span{font-size:13px;color:var(--mute)}.mini i{display:block;height:5px;width:36px;border-radius:9px;margin-bottom:10px}
.donut{display:flex;align-items:center;gap:22px;flex-wrap:wrap}.donut svg{width:150px;height:150px;flex:none}
.leg{flex:1;min-width:170px}.leg div{display:flex;align-items:center;gap:9px;padding:5px 0;font-size:14px}.leg i{width:11px;height:11px;border-radius:50%}.leg b{margin-left:auto}
.bar{display:flex;align-items:center;gap:12px;margin:12px 0;font-size:14px}.bar .lab{width:150px;flex:none;font-weight:600}.bar .lab small{display:block;color:var(--mute);font-weight:400;font-size:12px}
.track{position:relative;flex:1;height:11px;background:#f6ebf0;border-radius:99px}
.fill{position:absolute;left:0;top:0;bottom:0;border-radius:99px;background:linear-gradient(90deg,var(--plum2),var(--rose))}
.mk{position:absolute;top:-4px;bottom:-4px;width:3px;border-radius:2px;background:var(--plum)}
.hist{display:flex;align-items:flex-end;gap:4px;height:110px;margin:14px 0 4px}.hist i{flex:1;background:#f3cddb;min-height:2px;border-radius:7px 7px 3px 3px}.hist i.th{background:var(--plum2)}
.gh{display:flex;justify-content:space-between;align-items:baseline;margin:26px 4px 4px}.gh b{font:700 20px 'Fraunces',serif;color:var(--plum)}.gh span{color:var(--mute);font-size:13.5px}
.tag{display:inline-block;background:var(--tealsoft);color:#126b63;border-radius:99px;padding:5px 13px;font-size:13px;font-weight:600;margin:3px 5px 3px 0}
.lbl{font-size:11.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--mute);margin:14px 0 3px}
.fam{font-size:12px;font-weight:700;background:var(--lilac);color:var(--plum2);border-radius:99px;padding:3px 10px;margin-left:8px;vertical-align:middle}
.sum{border-radius:26px;padding:20px 24px;color:#fff;background:linear-gradient(135deg,#3b1147,#5e2373 60%,#b23a68 130%)}
.sum .big{font-size:40px}.sum small{opacity:.85}
.tl{position:relative;padding-left:26px}.tl:before{content:"";position:absolute;left:8px;top:8px;bottom:8px;width:2px;background:var(--line)}
.ev{position:relative;padding:8px 0 14px}.ev:before{content:"";position:absolute;left:-24px;top:14px;width:11px;height:11px;border-radius:50%;background:var(--rose);box-shadow:0 0 0 5px #fde3ec}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--mute)}
.ok{color:#126b63;font-weight:700}.bad{color:#b8325f;font-weight:700}
.proverb{text-align:center;margin:40px 0 6px;font:600 22px/1.3 'Fraunces',serif;color:var(--plum)}.proverb small{display:block;margin-top:5px;font:400 13.5px 'DM Sans';color:var(--mute)}
.fine{text-align:center;color:var(--mute);font-size:12.5px;margin-bottom:8px}
[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"]{border-radius:999px;font-weight:700;padding:.4rem 1rem;white-space:nowrap}
[data-testid="stBaseButton-secondary"] p,[data-testid="stBaseButton-primary"] p{overflow:visible;text-overflow:clip;white-space:nowrap}
[data-testid="stBaseButton-secondary"]{background:#fff;border:1px solid #ecd2df;color:var(--plum2)}
[data-testid="stBaseButton-secondary"]:hover{border-color:var(--rose);color:var(--rose);background:#fff}
[data-testid="stBaseButton-primary"]{background:var(--plum);border:1px solid var(--plum);color:#fff}
[data-testid="stBaseButton-primary"]:hover{background:var(--plum2);border-color:var(--plum2);color:#fff}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stDialog"] div[role="dialog"]{background:var(--blush);border-radius:28px}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:18px}
@media (max-width:640px){.block-container{padding-top:2.6rem}.hero:before{width:150px;height:150px;right:-56px;top:-56px;opacity:.35}.big{font-size:40px}.hero{padding:22px 20px 0;border-radius:26px}.spark{width:calc(100% + 40px);margin-left:-20px}.pillnote{display:none}.bar .lab{width:104px}.hello{font-size:25px}}
"""


def css() -> str:
    body = CSS.replace("__KANGA__", _uri(_KANGA)).replace("__MOTIF__", _uri(_MOTIF))
    return f"<style>{font_face_css()}{body}</style>"
