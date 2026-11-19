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
    WORK, DECISIONS, TREE, HIDDEN_LIST, STATS, SOW_TODO, SOW_OUT,
    LIVE, HIDDEN, ADMIN, BEHIND, OLD, IN, REV, OUT,
)

UPDATED = "November 19, 2026"
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
    f"<div class=dec><div class=dec-n>{i}</div><div><div class=dec-t>{e(t)}</div><p>{e(c)}</p></div><div class=who>{e(o)}</div></div>"
    for i, (t, c, o) in enumerate(DECISIONS, 1)
)
tree = "".join(
    f"<div class=branch><div class=area>{e(a)}<span class=count>{len(v)} version{'s' if len(v) > 1 else ''}</span></div><ol>"
    + "".join(f"<li><span class=td>{e(d)}</span><span>{e(t)}</span></li>" for d, t in v)
    + "</ol></div>"
    for a, v in TREE
)
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
:root {{ --navy:#1c2f6e; --crimson:#9b1b2e; --gold:#b8893b; --ink:#1d1d22; --muted:#66666f; --line:#e4e4ea; --soft:#f7f6f2; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:15px/1.5 -apple-system,"Helvetica Neue",Arial,sans-serif; color:var(--ink); background:#fff; }}
header.top {{ border-top:5px solid var(--crimson); background:var(--soft); }}
.wrap {{ max-width:1180px; margin:0 auto; padding:0 24px; }}
.top .wrap {{ padding-top:28px; padding-bottom:0; }}
h1 {{ margin:0; color:var(--navy); font-size:30px; letter-spacing:-0.01em; }}
.sub {{ color:var(--muted); margin:6px 0 18px; font-size:14px; }}
.sub a {{ color:var(--navy); }}
nav.tabs {{ display:flex; gap:4px; overflow-x:auto; }}
nav.tabs a {{ padding:10px 16px; text-decoration:none; color:var(--muted); font-weight:600; font-size:14px; border-bottom:3px solid transparent; white-space:nowrap; }}
nav.tabs a.on {{ color:var(--navy); border-color:var(--gold); }}
main {{ padding:32px 24px 60px; }}
section.tab {{ display:none; }} section.tab.on {{ display:block; }}
h2 {{ color:var(--navy); margin:0 0 6px; font-size:22px; }}
h3 {{ color:var(--navy); margin:0 0 8px; font-size:16px; }}
.lead {{ color:var(--muted); margin:0 0 18px; max-width:820px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:0 0 24px; }}
.stat {{ border:1px solid #e8dcc0; border-radius:10px; padding:14px; background:#fbf8f1; }}
.num {{ font-size:28px; font-weight:700; color:var(--crimson); }} .lab {{ color:var(--muted); font-size:13px; }}
.grid2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:18px; }}
.box {{ border:1px solid var(--line); border-radius:10px; padding:18px 20px; }}
.box ul {{ margin:0; padding-left:18px; }} .box li {{ margin:4px 0; }}
.bars {{ display:flex; height:12px; border-radius:6px; overflow:hidden; margin:10px 0 6px; }}
.bars span {{ display:block; }}
.bars .in, .key .in {{ background:#3f9a62; }} .bars .rev, .key .rev {{ background:#d9a03a; }} .bars .out, .key .out {{ background:var(--crimson); }}
.key {{ display:flex; flex-wrap:wrap; gap:12px; font-size:13px; color:var(--muted); }}
.key i {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:5px; vertical-align:-1px; }}
.pill {{ display:inline-block; padding:2px 9px; border-radius:10px; font-size:12px; font-weight:600; white-space:nowrap; }}
.live,.in {{ background:#e3f3e8; color:#17663a; }} .hidden,.rev {{ background:#fdf0d8; color:#8a5a00; }}
.admin {{ background:#e5ebfb; color:#1c3f9e; }} .behind {{ background:#ececf0; color:#4a4a55; }}
.old {{ background:#f3e6f7; color:#6a2380; }} .out {{ background:#fbe3e6; color:var(--crimson); }}
.filters {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:0 0 8px; font-size:13px; color:var(--muted); }}
.filters button {{ border:1px solid var(--line); background:#fff; border-radius:16px; padding:4px 11px; font:inherit; color:var(--ink); cursor:pointer; }}
.filters button span {{ color:var(--muted); }}
.filters button.on {{ background:var(--navy); border-color:var(--navy); color:#fff; }} .filters button.on span {{ color:#cfd6f0; }}
input.search {{ border:1px solid var(--line); border-radius:8px; padding:7px 11px; font:inherit; width:260px; max-width:100%; margin:0 0 12px; }}
.table {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th {{ text-align:left; background:var(--navy); color:#fff; padding:9px 10px; font-weight:600; position:sticky; top:0; }}
td {{ padding:8px 10px; border-top:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#fafafc; }}
.nowrap {{ white-space:nowrap; }} .muted {{ color:var(--muted); }} .strong {{ font-weight:600; }}
.count-line {{ font-size:13px; color:var(--muted); margin:8px 2px 0; }}
.dec {{ display:grid; grid-template-columns:34px 1fr auto; gap:12px; padding:14px 16px; border:1px solid var(--line); border-radius:10px; margin:0 0 10px; }}
.dec-n {{ width:28px; height:28px; border-radius:50%; background:var(--crimson); color:#fff; font-weight:700; display:grid; place-items:center; font-size:13px; }}
.dec-t {{ font-weight:700; }} .dec p {{ margin:3px 0 0; color:#44444c; }}
.who {{ font-weight:600; color:var(--navy); white-space:nowrap; font-size:14px; }}
.tree {{ columns:3 300px; column-gap:22px; }}
.branch {{ break-inside:avoid; margin:0 0 18px; border-left:3px solid var(--gold); padding-left:12px; }}
.area {{ font-weight:700; color:var(--navy); }} .count {{ color:var(--crimson); font-size:12px; font-weight:600; margin-left:8px; }}
.branch ol {{ list-style:none; margin:6px 0 0; padding:0; }}
.branch li {{ display:grid; grid-template-columns:76px 1fr; gap:6px; font-size:14px; padding:2px 0; }}
.branch li:last-child span:last-child {{ font-weight:700; }}
.td {{ color:var(--muted); }}
footer {{ color:var(--muted); font-size:13px; border-top:1px solid var(--line); padding:16px 0 30px; }}
@media (max-width:640px) {{ .dec {{ grid-template-columns:28px 1fr; }} .who {{ grid-column:2; }} }}
</style></head><body>
<header class=top><div class=wrap>
  <h1>LVTA Website: Project Tracker</h1>
  <p class=sub>Las Vegas Theatre Alliance &middot; Last updated {UPDATED} &middot; Staging site: <a href="{STAGING}" target=_blank rel=noopener>{STAGING.replace('https://', '')}</a></p>
  <nav class=tabs>
    <a href="#overview">Overview</a><a href="#work">Completed work</a><a href="#decisions">Needs a decision ({len(DECISIONS)})</a>
    <a href="#scope">Scope (SOW)</a><a href="#map">Change map</a>
  </nav>
</div></header>
<main class=wrap>

<section class=tab id=overview>
  <div class=stats>{stats}</div>
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
      <div class=key><span><i class=in></i>{scounts[IN]} in the SOW</span><span><i class=rev></i>{scounts[REV]} revisions after delivery</span><span><i class=out></i>{scounts[OUT]} beyond the SOW</span></div>
    </div>
    <div class=box>
      <h3>Built and ready, hidden for the fundraising launch</h3>
      <p class=muted style="margin:0 0 8px">One switch brings all of this back when LVTA is ready:</p>
      <ul>{hidden}</ul>
    </div>
  </div>
</section>

<section class=tab id=work>
  <h2>Completed work</h2>
  <p class=lead>Everything delivered since the project started, newest first. "PR" items are reviewed changes on GitHub; October items went in before pull requests were set up.</p>
  <div class=filters>Status: <button class=on data-status=all>All <span>{len(WORK)}</span></button>{status_filters}</div>
  <div class=filters>Scope: <button class=on data-scope=all>All <span>{len(WORK)}</span></button>{scope_filters}</div>
  <input class=search type=search placeholder="Search the work" aria-label="Search the work">
  <div class=table><table><thead><tr><th>Date</th><th>Ref</th><th>Area</th><th>Delivered</th><th>Status</th><th>Scope</th></tr></thead><tbody>{work_rows}</tbody></table></div>
  <p class=count-line id=shown></p>
</section>

<section class=tab id=decisions>
  <h2>Needs a decision or action</h2>
  <p class=lead>Open items before launch. Items 1 and 2 are Givebutter settings (Gary); the rest are board decisions.</p>
  {dec_cards}
</section>

<section class=tab id=scope>
  <h2>Statement of Work</h2>
  <p class=lead>The SOW (October 5, 2026) estimated 54 hours across four phases, including an 8-hour allowance for content revisions. Out-of-scope work was to be handled as a separate SOW or change order.</p>
  <div class=grid2>
    <div class=box><h3>Still to do from the SOW</h3><ul>{sow_todo}</ul></div>
    <div class=box><h3>Delivered beyond the SOW</h3><ul>{sow_out}</ul>
      <p class=muted style="margin:10px 0 0">Plus {scounts[REV]} revisions requested after delivery. <a href="#work" data-goto-scope=rev>See them in Completed work</a>.</p></div>
  </div>
</section>

<section class=tab id=map>
  <h2>Change map</h2>
  <p class=lead>Each part of the site with every version it has been through, oldest first. The bold line is what's live today.</p>
  <div class=tree>{tree}</div>
</section>

<footer>Sources: the GitHub history of LVTA-Development/lvta-website (PRs #1 to #23 and the October commits before them) and the project's request history.</footer>
</main>
<script>
(function () {{
  var tabs = document.querySelectorAll("nav.tabs a"), secs = document.querySelectorAll("section.tab");
  function show() {{
    var id = (location.hash || "#overview").slice(1);
    if (!document.getElementById(id)) id = "overview";
    secs.forEach(function (s) {{ s.classList.toggle("on", s.id === id); }});
    tabs.forEach(function (a) {{ a.classList.toggle("on", a.getAttribute("href") === "#" + id); }});
    window.scrollTo(0, 0);
  }}
  window.addEventListener("hashchange", show); show();

  var rows = document.querySelectorAll("#work tbody tr"), q = document.querySelector("input.search");
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
