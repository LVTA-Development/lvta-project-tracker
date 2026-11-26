"""Builds the LVTA website project tracker: one page (src/index.html) with
Overview, Completed work, Decisions, Scope (SOW) and Change map tabs, from the
same data as the PDF report (../report/data.py).

    python3 build.py           # writes src/index.html (plaintext, never published)
    npm run publish            # encrypts it into docs/ for GitHub Pages

Only docs/ (the encrypted page) is committed; src/ stays local."""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "report"))
from data import (  # noqa: E402
    WORK, DECISIONS, TREE, HIDDEN_LIST, STATS, SOW_TODO, SOW_OUT, COMMITS_BY_DAY,
    LIVE, HIDDEN, ADMIN, BEHIND, OLD, IN, REV, OUT,
)

UPDATED = "November 26, 2026"
SITE = os.path.join(HERE, "..", "lvta-website")
b64 = lambda f: __import__("base64").b64encode(open(os.path.join(SITE, f), "rb").read()).decode()
FONT_DISPLAY = b64("app/fonts/archivo-latin.woff2")
FONT_BODY = b64("app/fonts/inter-latin.woff2")
LOGO = b64("public/media/lvta-logo.png")
STAGING = "https://lvta-website-staging.vercel.app"
e = html.escape

CLS = {LIVE: "live", HIDDEN: "hidden", ADMIN: "admin", BEHIND: "behind", OLD: "old", IN: "in", REV: "rev", OUT: "out"}
pill = lambda s: f"<span class='pill {CLS[s]}'>{e(s)}</span>"

counts = {s: sum(1 for w in WORK if w[4] == s) for s in CLS if s in (LIVE, HIDDEN, ADMIN, BEHIND, OLD)}
scounts = {s: sum(1 for w in WORK if w[5] == s) for s in (IN, REV, OUT)}

stats = "".join(f"<div class=stat><div class=num>{e(n)}</div><div class=lab>{e(l)}</div></div>" for n, l in STATS)
work_rows = "".join(
    f"<tr data-status='{CLS[s]}' data-scope='{CLS[sc]}'><td class=nowrap>{e(d)}</td><td class='nowrap muted'>{e(r)}</td>"
    f"<td class=strong>{e(a)}</td><td>{e(w)}</td><td>{pill(s)}</td><td>{pill(sc)}</td></tr>"
    for d, r, a, w, s, sc in reversed(WORK)
)
dec_cards = "".join(
    f"<div class=dec><div class=dec-n>{i:02d}</div><div><div class=dec-t>{e(t)}</div><p>{e(c)}</p></div><div class=who>{e(o)}</div></div>"
    for i, (t, c, o) in enumerate(DECISIONS, 1)
)
def lane(area, versions):
    steps = []
    for i, (d, t) in enumerate(versions):
        now = i == len(versions) - 1
        steps.append(
            f"<li class='step{' now' if now else ''}'>"
            f"<div class=step-date>{e(d)}</div><div class=step-text>{e(t)}</div>"
            + ("<div class=now-tag>Live now</div>" if now else "")
            + "</li>"
        )
    n = len(versions)
    return (f"<div class=lane><div class=lane-head><h3>{e(area)}</h3>"
            f"<span class=lane-count>{n} version{'s' if n > 1 else ''}</span></div>"
            f"<ol class=steps>{''.join(steps)}</ol></div>")

tree = "".join(lane(a, v) for a, v in TREE)
import datetime as dt
from collections import defaultdict

MONTH_N = {"Oct": 10, "Nov": 11, "Dec": 12}
work_by_day = defaultdict(list)
for d, r, area, what, st, sc in WORK:
    mon, day = d.split()
    work_by_day[dt.date(2026, MONTH_N[mon], int(day))].append((area, what, st))
active = {dt.date.fromisoformat(k): v for k, v in COMMITS_BY_DAY.items()}
days = sorted(set(active) | set(work_by_day))
TODAY = max(days)

def level(n):
    return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 10 else 4

def month_grid(year, month):
    first = dt.date(year, month, 1)
    nxt = dt.date(year + (month == 12), month % 12 + 1, 1)
    cells = ["<div class=dow>" + x + "</div>" for x in ("S", "M", "T", "W", "T", "F", "S")]
    cells += ["<div class='day pad'></div>"] * ((first.weekday() + 1) % 7)
    d = first
    while d < nxt:
        n = active.get(d, 0)
        items = work_by_day.get(d, [])
        # A day with only non-code work (deploys, database changes, work on
        # other sites) is lit by how many items were delivered that day.
        bright = n if n else len(items)
        old = any(st == OLD for _, _, st in items)
        on = n or items
        order = days.index(d) if d in days else 0
        detail = ""
        if on:
            label = d.strftime("%A, %B %-d")
            parts = [f"<div class=pop-d>{e(label)}</div>"]
            if n:
                parts.append(f"<div class=pop-n>{n} code change{'s' if n > 1 else ''}</div>")
            elif items:
                parts.append(f"<div class=pop-n>{len(items)} update{'s' if len(items) > 1 else ''}</div>")
            parts += [f"<div class=pop-i><b>{e(a)}</b> {e(w)}</div>" for a, w, _ in items[:4]]
            if len(items) > 4:
                parts.append(f"<div class=pop-n>+ {len(items) - 4} more</div>")
            detail = "<div class=pop>" + "".join(parts) + "</div>"
        cls = f"day l{level(bright)}" + (" on" if on else "") + (" old" if old else "") + (" weekend" if d.weekday() >= 5 else "") + (" today" if d == TODAY else "")
        attr = f" tabindex=0 style='--i:{order}'" if on else ""
        cells.append(f"<div class='{cls}'{attr}><span>{d.day}</span>{detail}</div>")
        d += dt.timedelta(days=1)
    return (f"<div class=month><div class='label month-name'>{first.strftime('%B %Y')}</div>"
            f"<div class=mgrid>{''.join(cells)}</div></div>")

calendar = month_grid(2026, 10) + month_grid(2026, 11)
weekend_days = sum(1 for d in days if d.weekday() >= 5)
busiest = max(active, key=active.get)
hidden = "".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in HIDDEN_LIST)
sow_todo = "".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in SOW_TODO)
sow_out = "".join(f"<li>{e(x)}</li>" for x in SOW_OUT)
filters = lambda kind, opts: "".join(
    f"<button data-{kind}='{CLS[o]}'>{e(o)} <span>{n}</span></button>" for o, n in opts
)
status_filters = filters("status", [(s, counts[s]) for s in (LIVE, ADMIN, HIDDEN, BEHIND, OLD)])
scope_filters = filters("scope", [(s, scounts[s]) for s in (IN, REV, OUT)])

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<meta name=robots content="noindex, nofollow">
<title>LVTA Website: Project Tracker</title>
<style>
@font-face {{ font-family:"Archivo"; src:url(data:font/woff2;base64,{FONT_DISPLAY}) format("woff2"); font-weight:400 600; font-display:swap; }}
@font-face {{ font-family:"Inter"; src:url(data:font/woff2;base64,{FONT_BODY}) format("woff2"); font-weight:100 900; font-display:swap; }}
:root {{ --navy:#1c2f6e; --crimson:#9b1b2e; --crimson-deep:#7a1323; --gold:#b8893b; --gold-lt:#f0b45a; --cream:#f6d7a0;
  --stage:#0c0709; --ink:#1d1d22; --muted:#6b6b75; --line:#e7e2d6; --paper:#faf8f3; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:15px/1.55 "Inter",-apple-system,sans-serif; color:var(--ink); background:var(--paper); }}
.display {{ font-family:"Archivo",sans-serif; }}
.label {{ font-family:"Archivo",sans-serif; font-size:11.5px; letter-spacing:.22em; text-transform:uppercase; font-weight:500; }}
.wrap {{ max-width:1200px; margin:0 auto; padding:0 28px; }}

/* The stage */
header.stage {{ position:relative; isolation:isolate; overflow:hidden; background:var(--stage); color:#fff; }}
header.stage::before {{ content:""; position:absolute; inset:0; z-index:-1;
  background:radial-gradient(ellipse 55% 70% at 50% 0%,rgba(240,180,90,.24),transparent 72%),
    linear-gradient(90deg,rgba(74,12,24,.75),transparent 16%,transparent 84%,rgba(74,12,24,.75)); }}
header.stage::after {{ content:""; position:absolute; inset:0; z-index:-1; opacity:.5;
  background:repeating-linear-gradient(90deg,rgba(155,27,46,.16) 0 2px,transparent 2px 54px);
  -webkit-mask-image:linear-gradient(180deg,#000,transparent 80%); mask-image:linear-gradient(180deg,#000,transparent 80%); }}
.stage .wrap {{ padding-top:30px; }}
.brandbar {{ display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }}
.brandbar img {{ height:46px; filter:brightness(0) invert(1); }}
.brandbar a.site {{ color:var(--cream); text-decoration:none; border:1px solid rgba(184,137,59,.55); border-radius:999px; padding:7px 16px; }}
.brandbar a.site:hover {{ background:rgba(184,137,59,.15); }}
.hero {{ text-align:center; padding:34px 0 26px; }}
.hero .label {{ color:var(--gold-lt); }}
.hero h1 {{ font-family:"Archivo",sans-serif; font-weight:300; text-transform:uppercase; letter-spacing:.05em; line-height:1;
  font-size:clamp(34px,6vw,68px); margin:12px 0 0; text-shadow:0 0 50px rgba(240,180,90,.35); }}
.ornament {{ display:flex; align-items:center; justify-content:center; gap:10px; margin:16px 0 0; }}
.ornament i {{ display:block; height:1px; width:56px; background:rgba(184,137,59,.7); }}
.ornament b {{ display:block; width:6px; height:6px; transform:rotate(45deg); background:var(--gold); }}
.hero p {{ color:rgba(255,255,255,.62); margin:14px 0 0; font-size:14px; }}
nav.tabs {{ display:flex; justify-content:center; gap:4px; overflow-x:auto; border-top:1px solid rgba(255,255,255,.1); }}
nav.tabs a {{ padding:15px 16px 13px; text-decoration:none; color:rgba(255,255,255,.62); border-bottom:2px solid transparent; white-space:nowrap; }}
nav.tabs a:hover {{ color:#fff; }}
nav.tabs a.on {{ color:var(--cream); border-color:var(--gold-lt); }}
header.stage .floor {{ height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); }}

main {{ padding:40px 28px 70px; }}
section.tab {{ display:none; }} section.tab.on {{ display:block; }}
.sec-head {{ margin:0 0 20px; }}
.sec-head .label {{ color:var(--crimson); }}
h2 {{ font-family:"Archivo",sans-serif; font-weight:400; font-size:30px; letter-spacing:-.005em; color:var(--ink); margin:6px 0 6px; }}
h3 {{ font-family:"Archivo",sans-serif; color:var(--ink); margin:0 0 10px; font-size:16px; font-weight:600; }}
.lead {{ color:var(--muted); margin:0; max-width:780px; }}
a {{ color:var(--crimson); }}

.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin:0 0 26px; }}
.stat {{ background:#fff; border:1px solid var(--line); border-top:3px solid var(--gold); border-radius:10px; padding:16px; }}
.num {{ font-family:"Archivo",sans-serif; font-size:32px; font-weight:500; color:var(--crimson); line-height:1.1; }}
.lab {{ color:var(--muted); font-size:13px; margin-top:4px; }}
.grid2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:18px; }}
.box {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:22px 24px; }}
.box ul {{ margin:0; padding-left:18px; }} .box li {{ margin:5px 0; }} .box li::marker {{ color:var(--gold); }}
.box.dark {{ background:var(--stage); color:rgba(255,255,255,.82); border-color:#2a1d16;
  background-image:radial-gradient(ellipse 70% 60% at 50% 0%,rgba(240,180,90,.16),transparent 70%); }}
.box.dark h3 {{ color:var(--cream); }} .box.dark b {{ color:#fff; }} .box.dark .muted {{ color:rgba(255,255,255,.55); }}
.bars {{ display:flex; height:12px; border-radius:6px; overflow:hidden; margin:12px 0 8px; }}
.bars span {{ display:block; }}
.bars .in, .key .in {{ background:#3f9a62; }} .bars .rev, .key .rev {{ background:#d9a03a; }} .bars .out, .key .out {{ background:var(--crimson); }}
.key {{ display:flex; flex-wrap:wrap; gap:14px; font-size:13px; color:var(--muted); }}
.key i {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; vertical-align:-1px; }}

.pill {{ display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; white-space:nowrap; }}
.live,.in {{ background:#e3f3e8; color:#17663a; }} .hidden,.rev {{ background:#fdf0d8; color:#8a5a00; }}
.admin {{ background:#e5ebfb; color:#1c3f9e; }} .behind {{ background:#ececf0; color:#4a4a55; }}
.old {{ background:#f3e6f7; color:#6a2380; }} .out {{ background:#fbe3e6; color:var(--crimson); }}
.filters {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:0 0 8px; font-size:13px; color:var(--muted); }}
.filters .label {{ width:62px; font-size:10.5px; }}
.filters button {{ border:1px solid var(--line); background:#fff; border-radius:999px; padding:5px 12px; font:inherit; color:var(--ink); cursor:pointer; }}
.filters button span {{ color:var(--muted); }}
.filters button.on {{ background:var(--crimson); border-color:var(--crimson); color:#fff; }} .filters button.on span {{ color:#f3c9cf; }}
input.search {{ border:1px solid var(--line); border-radius:999px; padding:8px 16px; font:inherit; width:280px; max-width:100%; margin:6px 0 14px; background:#fff; }}
.table {{ overflow-x:auto; border:1px solid var(--line); border-radius:12px; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th {{ text-align:left; background:var(--stage); color:var(--cream); padding:11px 12px; font-family:"Archivo",sans-serif; font-weight:500;
  font-size:11px; letter-spacing:.18em; text-transform:uppercase; }}
td {{ padding:9px 12px; border-top:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#fcfbf8; }}
.nowrap {{ white-space:nowrap; }} .muted {{ color:var(--muted); }} .strong {{ font-weight:600; }}
.count-line {{ font-size:13px; color:var(--muted); margin:10px 2px 0; }}

.dec {{ display:grid; grid-template-columns:40px 1fr auto; gap:14px; align-items:start; padding:16px 18px; background:#fff;
  border:1px solid var(--line); border-left:3px solid var(--crimson); border-radius:10px; margin:0 0 10px; }}
.dec-n {{ font-family:"Archivo",sans-serif; font-size:24px; font-weight:300; color:var(--gold); line-height:1.1; }}
.dec-t {{ font-weight:600; }} .dec p {{ margin:4px 0 0; color:#4a4a52; }}
.who {{ font-family:"Archivo",sans-serif; font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--crimson);
  white-space:nowrap; border:1px solid rgba(155,27,46,.3); border-radius:999px; padding:4px 11px; }}

/* Change map: each area reads left to right, oldest to live now */
.howto {{ display:flex; align-items:center; gap:10px; color:var(--muted); font-size:13px; margin:14px 0 22px; }}
.howto .arrow {{ flex:0 0 60px; height:1px; background:var(--gold); position:relative; }}
.howto .arrow::after {{ content:""; position:absolute; right:-1px; top:-3px; border:3.5px solid transparent; border-left:6px solid var(--gold); }}
.lane {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:18px 20px 20px; margin:0 0 14px; }}
.lane-head {{ display:flex; align-items:baseline; gap:12px; margin:0 0 14px; }}
.lane-head h3 {{ margin:0; font-size:18px; }}
.lane-count {{ color:var(--crimson); font-size:12px; font-weight:600; }}
.steps {{ list-style:none; margin:0; padding:0 0 4px; display:flex; gap:34px; overflow-x:auto; }}
.step {{ position:relative; flex:1 1 0; min-width:150px; max-width:260px; border:1px solid var(--line); border-radius:10px; padding:11px 13px; background:var(--paper); }}
.step:not(:last-child)::after {{ content:""; position:absolute; top:50%; right:-27px; width:20px; height:1px; background:var(--gold); }}
.step:not(:last-child)::before {{ content:""; position:absolute; top:calc(50% - 4px); right:-28px; border:4px solid transparent; border-left:6px solid var(--gold); }}
.step-date {{ font-family:"Archivo",sans-serif; font-size:10.5px; letter-spacing:.2em; text-transform:uppercase; color:var(--gold); font-weight:600; }}
.step-text {{ font-size:13.5px; margin-top:4px; color:#3d3d45; }}
.step.now {{ background:var(--stage); border-color:var(--stage); color:#fff;
  background-image:radial-gradient(ellipse 90% 70% at 50% 0%,rgba(240,180,90,.22),transparent 72%); }}
.step.now .step-text {{ color:#fff; font-weight:500; }} .step.now .step-date {{ color:var(--gold-lt); }}
.now-tag {{ display:inline-block; margin-top:8px; font-family:"Archivo",sans-serif; font-size:10px; letter-spacing:.2em; text-transform:uppercase;
  color:var(--stage); background:var(--gold-lt); border-radius:999px; padding:2px 9px; font-weight:600; }}

/* Work calendar */
.cal {{ margin:0 0 22px; }}
.cal-head {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }}
.cal-head p {{ margin:0; max-width:760px; font-size:14px; }}
.replay {{ font-family:"Archivo",sans-serif; font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--cream);
  background:none; border:1px solid rgba(184,137,59,.55); border-radius:999px; padding:7px 14px; cursor:pointer; white-space:nowrap; }}
.replay:hover {{ background:rgba(184,137,59,.15); }}
.months {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:26px 40px; margin:20px 0 14px; }}
.month-name {{ color:var(--gold-lt); margin:0 0 10px; }}
.mgrid {{ display:grid; grid-template-columns:repeat(7,1fr); gap:6px; }}
.dow {{ font-family:"Archivo",sans-serif; font-size:10px; letter-spacing:.15em; color:rgba(255,255,255,.35); text-align:center; }}
.day {{ position:relative; aspect-ratio:1; border-radius:7px; background:rgba(255,255,255,.04); display:flex; align-items:flex-start;
  justify-content:flex-end; padding:5px 6px; font-size:11px; color:rgba(255,255,255,.3); }}
.day.pad {{ background:none; }}
.day.weekend:not(.on) {{ background:rgba(255,255,255,.025); }}
.day.on {{ cursor:pointer; color:#fff; font-weight:600; outline:none; }}
.day.l1 {{ background:rgba(240,180,90,.28); }} .day.l2 {{ background:rgba(240,180,90,.5); }}
.day.l3 {{ background:rgba(240,180,90,.75); color:var(--stage); }} .day.l4 {{ background:var(--gold-lt); color:var(--stage); box-shadow:0 0 22px rgba(240,180,90,.6); }}
.day.on.l0 {{ background:rgba(255,255,255,.08); }}
.day.old {{ box-shadow:inset 0 0 0 2px #c58be0; }}
.day.l4.old, .day.l3.old {{ box-shadow:inset 0 0 0 2px #c58be0, 0 0 22px rgba(240,180,90,.5); }}
.day.today::after {{ content:""; position:absolute; left:6px; bottom:6px; width:5px; height:5px; border-radius:50%; background:var(--crimson); box-shadow:0 0 0 2px #fff; }}
.cal.play .day.on {{ animation:light .55s cubic-bezier(.2,.7,.2,1) both; animation-delay:calc(var(--i) * 90ms + 150ms); }}
@keyframes light {{ from {{ opacity:0; transform:scale(.6); filter:brightness(2.2); }} 60% {{ opacity:1; transform:scale(1.08); }} to {{ opacity:1; transform:scale(1); filter:none; }} }}
.pop {{ display:none; position:absolute; z-index:5; bottom:calc(100% + 8px); left:50%; transform:translateX(-50%); width:270px;
  background:#fff; color:var(--ink); border-radius:10px; padding:11px 13px; box-shadow:0 14px 40px rgba(0,0,0,.45); font-weight:400; text-align:left; cursor:auto; }}
.pop::after {{ content:""; position:absolute; top:100%; left:50%; margin-left:-6px; border:6px solid transparent; border-top-color:#fff; }}
.day:hover .pop, .day:focus .pop, .day:focus-within .pop {{ display:block; }}
.mgrid > .day:nth-child(7n+1) .pop, .mgrid > .day:nth-child(7n+2) .pop {{ left:0; transform:none; }}
.mgrid > .day:nth-child(7n+1) .pop::after, .mgrid > .day:nth-child(7n+2) .pop::after {{ left:18px; }}
.mgrid > .day:nth-child(7n) .pop, .mgrid > .day:nth-child(7n+6) .pop {{ left:auto; right:0; transform:none; }}
.mgrid > .day:nth-child(7n) .pop::after, .mgrid > .day:nth-child(7n+6) .pop::after {{ left:auto; right:12px; }}
.pop-d {{ font-family:"Archivo",sans-serif; font-weight:600; font-size:13px; }}
.pop-n {{ color:var(--crimson); font-size:12px; font-weight:600; margin:2px 0 4px; }}
.pop-i {{ font-size:12.5px; line-height:1.4; margin:4px 0 0; color:#3d3d45; }}
.box.dark .pop b {{ color:var(--crimson); }}
.cal-key {{ display:flex; align-items:center; flex-wrap:wrap; gap:6px; font-size:12px; color:rgba(255,255,255,.55); }}
.cal-key i {{ display:inline-block; width:14px; height:14px; border-radius:4px; }}
.cal-key .l1 {{ background:rgba(240,180,90,.28); }} .cal-key .l2 {{ background:rgba(240,180,90,.5); }}
.cal-key .l3 {{ background:rgba(240,180,90,.75); }} .cal-key .l4 {{ background:var(--gold-lt); }}
.cal-key .old-key {{ box-shadow:inset 0 0 0 2px #c58be0; }}
.cal-key .sep {{ width:16px; }}
.scope-note {{ font-size:13px; color:var(--muted); margin:6px 0 4px; max-width:860px; }}
@media (prefers-reduced-motion: reduce) {{ .cal.play .day.on {{ animation:none; }} }}
footer {{ color:var(--muted); font-size:13px; text-align:center; padding:26px 0 36px; border-top:1px solid var(--line); }}
@media (max-width:640px) {{
  .dec {{ grid-template-columns:30px 1fr; }} .who {{ grid-column:2; justify-self:start; }}
  .steps {{ flex-direction:column; gap:14px; overflow:visible; }} .step {{ max-width:none; }}
  .howto .arrow {{ display:none; }}
  .step:not(:last-child)::after {{ top:auto; bottom:-12px; right:auto; left:24px; width:1px; height:10px; }}
  .step:not(:last-child)::before {{ top:auto; bottom:-17px; right:auto; left:20px; border:4px solid transparent; border-top:6px solid var(--gold); }}
}}
</style></head><body>
<header class=stage><div class=wrap>
  <div class=brandbar>
    <img src="data:image/png;base64,{LOGO}" alt="Las Vegas Theatre Alliance">
    <a class="site label" href="{STAGING}" target=_blank rel=noopener>View the staging site</a>
  </div>
  <div class=hero>
    <div class=label>Las Vegas Theatre Alliance &middot; Website</div>
    <h1>Project Tracker</h1>
    <div class=ornament aria-hidden=true><i></i><b></b><i></i></div>
    <p>Last updated {UPDATED}</p>
  </div>
  <nav class="tabs label">
    <a href="#overview">Overview</a><a href="#work">Completed work</a><a href="#decisions">Needs a decision ({len(DECISIONS)})</a>
    <a href="#scope">Scope (SOW)</a><a href="#map">Change map</a>
  </nav>
</div><div class=floor></div></header>
<main class=wrap>

<section class=tab id=tab-overview>
  <div class=stats>{stats}</div>
  <div class="box dark cal" id=calendar>
    <div class=cal-head>
      <div><h3>When the work happened</h3>
        <p class=muted>{len(days)} working days from {days[0].strftime('%B %-d')} to {TODAY.strftime('%B %-d')}, {weekend_days} of them on a weekend. The brighter the day, the more changes went in; the busiest was {busiest.strftime('%B %-d')} with {active[busiest]}. Hover or tap a day to see what was done.</p></div>
      <button class=replay type=button>Replay</button>
    </div>
    <div class=months>{calendar}</div>
    <div class=cal-key><span>Fewer changes</span><i class=l1></i><i class=l2></i><i class=l3></i><i class=l4></i><span>More</span>
      <span class=sep></span><i class='old-key'></i><span>Fixes on the old lvta.org site</span></div>
  </div>
  <div class=grid2>
    <div class=box>
      <h3>Where things stand</h3>
      <ul>
        <li>The fundraising site is complete on staging: hero, mission, ACT ONE campaign, event and Donate, with the board's 11/17 campaign summary word for word.</li>
        <li>{len(WORK)} items delivered. {counts[LIVE]} are live on the public site, {counts[ADMIN]} are in the admin and member area, {counts[HIDDEN]} are built and hidden for the fundraising launch, {counts[BEHIND]} are behind the scenes, and {counts[OLD]} is a round of fixes on the old lvta.org site.</li>
        <li>An admin panel lets LVTA change site copy, the event, board profiles and the progress bar without a developer.</li>
        <li>Every change is checked by 337 automated tests before it reaches the site.</li>
        <li><a href="#decisions">{len(DECISIONS)} items</a> need a decision or an action before launch.</li>
      </ul>
      <h3 style="margin-top:16px">Against the Statement of Work</h3>
      <div class=bars>
        <span class=in style="flex:{scounts[IN]}"></span><span class=rev style="flex:{scounts[REV]}"></span><span class=out style="flex:{scounts[OUT]}"></span>
      </div>
      <div class=key><span><i class=in></i>{scounts[IN]} in the SOW</span><span><i class=rev></i>{scounts[REV]} revisions to work already built</span><span><i class=out></i>{scounts[OUT]} beyond the SOW</span></div>
    </div>
    <div class="box dark">
      <h3>Built and ready, hidden for the fundraising launch</h3>
      <p class=muted style="margin:0 0 10px">One switch brings all of this back when LVTA is ready:</p>
      <ul>{hidden}</ul>
    </div>
  </div>
</section>

<section class=tab id=tab-work>
  <div class=sec-head><div class=label>Delivered</div><h2>Completed work</h2>
  <p class=lead>Everything delivered since the project started, newest first. "PR" items are reviewed changes on GitHub; October items went in before pull requests were set up.</p></div>
  <div class=filters><span class=label>Status</span><button class=on data-status=all>All <span>{len(WORK)}</span></button>{status_filters}</div>
  <div class=filters><span class=label>Scope</span><button class=on data-scope=all>All <span>{len(WORK)}</span></button>{scope_filters}</div>
  <p class=scope-note><b>In SOW</b> is listed in the Statement of Work. <b>Revision</b> is a change to something that was already built and shown, such as resizing the logo again or re-editing a video; the SOW allows 8 hours of these. <b>Beyond SOW</b> is work the SOW doesn't cover.</p>
  <input class=search type=search placeholder="Search the work" aria-label="Search the work">
  <div class=table><table><thead><tr><th>Date</th><th>Ref</th><th>Area</th><th>Delivered</th><th>Status</th><th>Scope</th></tr></thead><tbody>{work_rows}</tbody></table></div>
  <p class=count-line id=shown></p>
</section>

<section class=tab id=tab-decisions>
  <div class=sec-head><div class=label>Before launch</div><h2>Needs a decision or action</h2>
  <p class=lead>Open items before launch. Items 1 and 2 are Givebutter settings (Gary); the rest are board decisions.</p></div>
  {dec_cards}
</section>

<section class=tab id=tab-scope>
  <div class=sec-head><div class=label>Scope</div><h2>Statement of Work</h2>
  <p class=lead>The SOW (October 5, 2026) estimated 54 hours across four phases, including an 8-hour allowance for content revisions. Out-of-scope work was to be handled as a separate SOW or change order.</p></div>
  <div class=grid2>
    <div class=box><h3>Still to do from the SOW</h3><ul>{sow_todo}</ul></div>
    <div class=box><h3>Delivered beyond the SOW</h3><ul>{sow_out}</ul>
      <p class=muted style="margin:10px 0 0">Plus {scounts[REV]} revisions: changes to work that was already built and shown. <a href="#work" data-goto-scope=rev>See them in Completed work</a>.</p></div>
  </div>
</section>

<section class=tab id=tab-map>
  <div class=sec-head><div class=label>How the site evolved</div><h2>Change map</h2>
  <p class=lead>Every version each part of the site has been through, from the first build to what's live today.</p></div>
  <div class=howto><span>Oldest</span><span class=arrow></span><span>Live now</span></div>
  <div class=tree>{tree}</div>
</section>

<footer>Sources: the GitHub history of LVTA-Development/lvta-website (PRs #1 to #23 and the October commits before them) and the project's request history.</footer>
</main>
<script>
if ("scrollRestoration" in history) history.scrollRestoration = "manual";
var cal = document.getElementById("calendar");
function play() {{
  if (!cal) return;
  cal.classList.remove("play"); void cal.offsetWidth; cal.classList.add("play");
}}
(function () {{
  document.querySelector(".replay").addEventListener("click", play);
  var tabs = document.querySelectorAll("nav.tabs a"), secs = document.querySelectorAll("section.tab");
  function show() {{
    var id = (location.hash || "#overview").slice(1);
    if (!document.getElementById("tab-" + id)) id = "overview";
    secs.forEach(function (s) {{ s.classList.toggle("on", s.id === "tab-" + id); }});
    tabs.forEach(function (a) {{ a.classList.toggle("on", a.getAttribute("href") === "#" + id); }});
    setTimeout(function () {{ window.scrollTo(0, 0); }}, 0);
    if (id === "overview") play();
  }}
  window.addEventListener("hashchange", show); show();

  var rows = document.querySelectorAll("#tab-work tbody tr"), q = document.querySelector("input.search");
  var f = {{ status: "all", scope: "all" }};
  function apply() {{
    var t = q.value.toLowerCase(), n = 0;
    rows.forEach(function (r) {{
      var ok = (f.status === "all" || r.dataset.status === f.status) &&
               (f.scope === "all" || r.dataset.scope === f.scope) &&
               (!t || r.textContent.toLowerCase().indexOf(t) !== -1);
      r.style.display = ok ? "" : "none"; if (ok) n++;
    }});
    document.getElementById("shown").textContent = "Showing " + n + " of " + rows.length + " items";
  }}
  function pick(kind, val) {{
    f[kind] = val;
    document.querySelectorAll("[data-" + kind + "]").forEach(function (b) {{
      if (b.tagName === "BUTTON") b.classList.toggle("on", b.dataset[kind] === val);
    }});
    apply();
  }}
  ["status", "scope"].forEach(function (kind) {{
    document.querySelectorAll("button[data-" + kind + "]").forEach(function (b) {{
      b.addEventListener("click", function () {{ pick(kind, b.dataset[kind]); }});
    }});
  }});
  document.querySelectorAll("[data-goto-scope]").forEach(function (a) {{
    a.addEventListener("click", function () {{ pick("status", "all"); pick("scope", a.dataset.gotoScope); }});
  }});
  q.addEventListener("input", apply); apply();
}})();
</script>
</body></html>"""

os.makedirs(os.path.join(HERE, "src"), exist_ok=True)
open(os.path.join(HERE, "src", "index.html"), "w").write(page)
print("src/index.html", len(WORK), "items,", len(DECISIONS), "decisions")
