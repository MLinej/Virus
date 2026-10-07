"""
ViraGuard: virus spread, mutation and isolation on a population grid.

    Home       short description of the project
    Spread     multi-source BFS: how many days until everyone is infected
    Mutation   a family tree of variants, each compared with its parent (LCS, Edit Distance)
    Isolation  backtracking finds the K people whose isolation shrinks the outbreak most

Run with:  streamlit run app.py
"""

import math

import streamlit as st

from algorithms.backtracking import best_isolation
from algorithms.bfs import infected_per_day, multi_source_bfs, outbreak_summary
from algorithms.edit_distance import edit_distance_table, edit_operations
from algorithms.lcs import lcs_table
from simulation.mutation import evolve
from simulation.population import generate_population
from visualization.grid import curve_figure, grid_figure
from visualization.tree import tree_figure

MUTATION_EVERY = 2        # days between mutation waves
PLOT_CONFIG = {"displayModeBar": False}
PAGES = {"spread": "SPREAD", "mutation": "MUTATION", "isolation": "ISOLATION"}

st.set_page_config(page_title="ViraGuard", page_icon="🦠", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------------------
# Theme (light gray, black ink, dark purple + lime accents, mono type)
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=JetBrains+Mono:wght@400;500;700&display=swap');
:root {
  --bg: #f2f2ef; --panel: #f7f7f4; --ink: #0d0d0d; --muted: #5f5f5a;
  --line: rgba(13,13,13,0.14); --purple: #6d28d9; --lime: #d4f53c;
}
html, body, .stApp, .stApp * {font-family: 'JetBrains Mono', ui-monospace, monospace;}
.stApp [data-testid="stIconMaterial"] {font-family: 'Material Symbols Rounded' !important;}
header[data-testid="stHeader"], [data-testid="stSidebarCollapsedControl"] {display: none;}
.block-container {max-width: 1240px; padding: 1.2rem 2rem 0 2rem;}
.stApp p, .stApp li {font-size: 0.98rem;}

/* panels */
[class*="st-key-panel"] {border: 1px solid var(--line); background: var(--panel);
                         padding: 1.8rem 2rem; border-radius: 4px; margin-bottom: 0.5rem;}

/* navbar */
.st-key-nav {border-bottom: 1px solid var(--line); padding: 0.4rem 0 0.9rem 0;
             margin-bottom: 1rem;}
.st-key-nav [class*="st-key-go_"] {display: flex; justify-content: center; position: relative;
                                   width: 100% !important;}
.st-key-nav [class*="st-key-go_"] > *, .st-key-nav [class*="st-key-go_"] button {
  width: auto !important; flex: 0 0 auto !important;}
.st-key-go_mutation::before, .st-key-go_isolation::before {
  content: "/"; position: absolute; left: -0.5rem; top: 50%; transform: translateY(-50%);
  color: var(--purple); font-size: 1rem;}
.st-key-nav [class*="st-key-go_"] button {
  background: transparent !important; border: none !important; box-shadow: none !important;
  border-radius: 0 !important; color: var(--ink) !important; padding: 0.25rem 0 !important;
  min-height: 0 !important; border-bottom: 2px solid transparent !important;}
.st-key-nav [class*="st-key-go_"] button p {font-size: 0.9rem; letter-spacing: 0.1em;}
.st-key-nav [class*="st-key-go_"] button:hover {color: var(--purple) !important;}
.st-key-nav [class*="st-key-go_"] button[data-testid="stBaseButton-primary"] {
  color: var(--purple) !important; border-bottom: 2px solid var(--purple) !important;}
/* buttons */
.stApp button[data-testid="stBaseButton-primary"] {
  background: var(--ink); border: 1px solid var(--ink); color: #fff; border-radius: 0;
  padding: 0.8rem 1.3rem;}
.stApp button[data-testid="stBaseButton-primary"]:hover {background: var(--purple);
  border-color: var(--purple); color: #fff;}
.stApp button p {font-size: 0.88rem; letter-spacing: 0.08em; text-transform: uppercase;}
.stApp button[data-testid="stBaseButton-secondary"] {border-radius: 0; border: 1px solid var(--ink);
  background: transparent; color: var(--ink); padding: 0.8rem 1.3rem;}
.stApp button[data-testid="stBaseButton-secondary"]:hover {border-color: var(--purple);
  color: var(--purple);}
.stApp button[data-testid="stBaseButton-tertiary"] {color: var(--ink); padding: 0.8rem 0;}
.stApp button[data-testid="stBaseButton-tertiary"]:hover {color: var(--purple);}
.st-key-find button {background: var(--purple) !important; border-color: var(--purple) !important;}
.st-key-find button:hover {background: var(--ink) !important; border-color: var(--ink) !important;}

/* widgets */
[data-testid="stWidgetLabel"] p {font-size: 0.8rem !important; letter-spacing: 0.12em;
                                 text-transform: uppercase; color: var(--muted);}
[data-testid="stExpander"] details {border-radius: 0; border: 1px solid var(--line);
                                    background: var(--panel);}
[data-testid="stExpander"] summary p {font-size: 0.86rem; letter-spacing: 0.1em;
                                      text-transform: uppercase;}

/* hero (home page) */
.st-key-panel_hero {margin-top: 1.5rem;}
.idx {color: var(--purple); font-size: 0.9rem; letter-spacing: 0.1em; margin-bottom: 1.1rem;}
.display {font-family: 'Anton', Impact, sans-serif !important; font-size: 6rem;
          line-height: 0.98; letter-spacing: 0.005em; margin: 0; color: var(--ink);
          text-transform: uppercase; font-weight: 400;}
.kicker {color: var(--purple); font-weight: 700; font-size: 1rem; letter-spacing: 0.08em;
         margin: 1.5rem 0 1.1rem 0;}
.lead {font-size: 1rem; line-height: 1.85; max-width: 500px; margin-bottom: 1.5rem;}
.art {position: relative; height: 520px; overflow: hidden;
      background-image: linear-gradient(var(--line) 1px, transparent 1px),
                        linear-gradient(90deg, var(--line) 1px, transparent 1px);
      background-size: 48px 48px; background-position: center;}
.art img {position: absolute; left: 50%; top: 50%; width: 430px;
          transform: translate(-50%, -50%); filter: contrast(1.1);}
.px {position: absolute; display: block;}
.px.p {background: var(--purple); mix-blend-mode: multiply; opacity: 0.85;}
.px.l {background: var(--lime); mix-blend-mode: multiply;}
.px.k {background: var(--ink); opacity: 0.85;}
.px.o {border: 1px solid var(--purple);}
.plus {position: absolute; color: var(--ink); font-size: 1.05rem; line-height: 1;}
.plus.l {color: #a8c418;}
.chip {position: absolute; background: var(--panel); font-size: 0.82rem; line-height: 1.7;
       padding: 0.55rem 0.8rem; border: 1px solid var(--line);}
.chip i {font-style: normal; color: var(--purple);}
.coords {position: absolute; right: 0; top: 54%; background: rgba(212,245,60,0.22);
         border: 1px solid #b8d82a; font-size: 0.86rem; line-height: 1.75;
         padding: 0.65rem 0.95rem;}
.scn {position: absolute; right: 0.4rem; bottom: 0.3rem; font-size: 0.82rem;
      letter-spacing: 0.08em;}
.globe {position: absolute; right: 0.6rem; top: 0.6rem;}

/* sections & status */
.sec {font-size: 0.92rem; letter-spacing: 0.12em; margin-bottom: 1.2rem; text-transform: uppercase;}
.sec .num {color: var(--purple); margin-right: 1.1rem;}
.h2 {font-weight: 700; font-size: 1.2rem; letter-spacing: 0.06em; margin-bottom: 1rem;
     text-transform: uppercase;}
.row {display: grid; grid-template-columns: 11rem 1fr 7.5rem; align-items: center; gap: 1rem;
      font-size: 0.86rem; padding: 0.45rem 0; letter-spacing: 0.04em;}
.row .val {text-align: right;}
.bar {height: 9px; background: rgba(13,13,13,0.08);}
.bar span {display: block; height: 100%; background: var(--purple);}
.bar.dim span {background: var(--ink);}
.banner {background: var(--lime); padding: 0.75rem 1rem; font-size: 0.86rem; margin-top: 1rem;
         display: flex; justify-content: space-between; align-items: center;
         letter-spacing: 0.06em; font-weight: 500;}
.dot {width: 9px; height: 9px; border-radius: 50%; background: var(--ink); display: inline-block;}
.hint {color: var(--muted); font-size: 0.86rem; line-height: 1.7;}
.legend {display: flex; flex-wrap: wrap; gap: 1.4rem; font-size: 0.82rem; color: var(--muted);
         letter-spacing: 0.06em; margin-top: 0.5rem;}
.sw {display: inline-block; width: 11px; height: 11px; margin-right: 0.45rem; vertical-align: -1px;}

/* mutation */
.seq {white-space: nowrap; overflow-x: auto;}
.seq span {display: inline-block; width: 1.25em; text-align: center; font-size: 1.02rem;
           line-height: 1.8;}
.seq .sub-m {background: var(--purple); color: #fff;}
.seq .ins-m {background: var(--lime); color: var(--ink);}
.seq .del-m {background: var(--ink); color: #fff;}
.seq .tag {font-size: 0.8rem; color: var(--muted); width: 3.2rem; text-align: left;}
.lineage {font-size: 0.9rem; letter-spacing: 0.04em; margin-bottom: 1rem;}
.lineage b {color: var(--purple);}
.card {border: 1px solid var(--line); background: var(--panel); padding: 1.1rem 1.3rem;
       margin-bottom: 0.8rem;}
.card-top {display: flex; justify-content: space-between; font-size: 0.86rem;
           letter-spacing: 0.08em; margin-bottom: 0.7rem;}
.card-top .num {color: var(--purple); margin-right: 0.9rem;}
.stats {display: flex; gap: 2rem; margin-top: 0.8rem; font-size: 0.84rem; letter-spacing: 0.06em;
        color: var(--muted); flex-wrap: wrap;}
.stats b {color: var(--ink); font-weight: 700;}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@st.cache_data
def build(n, sources, seed):
    pop = generate_population(n, seed=seed, sources=sources)
    day = multi_source_bfs(pop.adj, pop.sources)
    return pop, day


def html(s):
    st.markdown(s, unsafe_allow_html=True)


def section(num, title):
    html(f"<div class='sec'><span class='num'>/{num:02d}</span>{title}</div>")


def status_panel(title, rows, banner=None):
    """rows: (label, fraction 0..1 or None, value text, dim?)"""
    out = f"<div class='h2'>{title}</div>" if title else ""
    for label, frac, value, dim in rows:
        bar = ("<div></div>" if frac is None else
               f"<div class='bar{' dim' if dim else ''}'><span style='width:{100 * frac:.0f}%'>"
               f"</span></div>")
        out += f"<div class='row'><div>{label}</div>{bar}<div class='val'>{value}</div></div>"
    if banner:
        out += f"<div class='banner'><span>{banner}</span><span class='dot'></span></div>"
    html(out)


def alignment_html(parent, child, parent_name, child_name):
    """Parent and child genomes aligned, changed letters highlighted."""
    ops = edit_operations(parent, child)
    css = {"match": "", "sub": "sub-m", "del": "del-m", "ins": "ins-m"}
    top = "".join(f"<span class='{css[op]}'>{a}</span>" for op, a, _ in ops)
    bottom = "".join(f"<span class='{css[op]}'>{b}</span>" for op, _, b in ops)
    return (f"<div class='seq'><span class='tag'>{parent_name}</span>{top}</div>"
            f"<div class='seq'><span class='tag'>{child_name}</span>{bottom}</div>")


def describe_changes(parent, child):
    """Net changes between two genomes, read from the edit-distance alignment."""
    out, pos = [], 0
    for op, a, b in edit_operations(parent, child):
        if op != "ins":
            pos += 1
        if op == "sub":
            out.append(f"{a}→{b} AT {pos}")
        elif op == "del":
            out.append(f"−{a} AT {pos}")
        elif op == "ins":
            out.append(f"+{b} AFTER {pos}")
    return " · ".join(out)


def compare(parent, child):
    lcs = lcs_table(parent.genome, child.genome)[len(parent.genome)][len(child.genome)]
    similarity = lcs / max(len(parent.genome), len(child.genome))
    dist = edit_distance_table(parent.genome, child.genome)[len(parent.genome)][len(child.genome)]
    return lcs, similarity, dist


def go_to(page):
    st.session_state.page = page


def grid_legend(saved=False):
    items = [("#0d0d0d", "INITIALLY INFECTED"), ("#e03131", "INFECTED (NUMBER = DAY)"),
             ("#d9d9d4", "HEALTHY")]
    if saved:
        items.append(("#2f9e44", "SAVED BY ISOLATION"))
    out = "".join(f"<span><span class='sw' style='background:{c}'></span>{t}</span>"
                  for c, t in items)
    html(f"<div class='legend'>{out}<span><span style='margin-right:.45rem'>+</span>"
         f"EMPTY POSITION</span><span><span style='margin-right:.45rem;color:#a3a39e'>✕"
         f"</span>ISOLATED</span></div>")


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

if "page" not in st.session_state:          # allow links like ?page=mutation
    st.session_state.page = (st.query_params.get("page")
                             if st.query_params.get("page") in PAGES else "home")
for name, default in [("seed", 7), ("n", 40), ("src", 3), ("k", 3)]:
    st.session_state.setdefault(name, default)
    st.session_state[name] = st.session_state[name]     # keep values across pages

page = st.session_state.page
pop, day = build(st.session_state.n, st.session_state.src, st.session_state.seed)
infected, total_days = outbreak_summary(day)


# ---------------------------------------------------------------------------
# Home page: description on the left, virus on the right (no navbar)
# ---------------------------------------------------------------------------

if page == "home":
    with st.container(key="panel_hero"):
        left, right = st.columns([5, 6], gap="large", vertical_alignment="center")
        with left:
            html("<div class='idx'>/00 — OVERVIEW</div>"
                 "<div class='display'>TRACE.<br>MUTATE.<br>CONTAIN.</div>"
                 "<div class='kicker'>GRAPH-DRIVEN. ALGORITHMIC. SYNTHETIC.</div>"
                 "<div class='lead'>A virus spreads across a population graph one day at a "
                 "time using multi-source BFS. Every few days it mutates, and each variant is "
                 "compared with its parent using LCS and edit distance. Backtracking then "
                 "finds the people whose isolation shrinks the outbreak the most.</div>")
            b1, b2 = st.columns([1.2, 1])
            b1.button("EXPLORE SPREAD ↗", key="hero_spread", type="primary", on_click=go_to,
                      args=("spread",), width="stretch")
            b2.button("VIEW MUTATIONS ⌗", key="hero_mut", type="tertiary", on_click=go_to,
                      args=("mutation",))
        with right:
            px = [  # (class, left %, top %, size px)
                ("p", 62, 14, 34), ("p", 70, 22, 22), ("l", 74, 30, 18), ("k", 66, 9, 14),
                ("p", 20, 58, 28), ("l", 16, 66, 22), ("p", 26, 72, 16), ("o", 12, 48, 30),
                ("p", 58, 78, 26), ("l", 64, 84, 16), ("k", 36, 18, 12), ("p", 80, 62, 20),
                ("o", 72, 70, 36), ("l", 44, 12, 12), ("k", 28, 84, 14), ("p", 48, 86, 12)]
            squares = "".join(f"<span class='px {c}' style='left:{x}%;top:{y}%;width:{s}px;"
                              f"height:{s}px'></span>" for c, x, y, s in px)
            pluses = "".join(f"<span class='plus{' l' if i % 3 == 0 else ''}' "
                             f"style='left:{x}%;top:{y}%'>+</span>"
                             for i, (x, y) in enumerate([(8, 20), (88, 14), (14, 88), (90, 44),
                                                         (52, 6), (6, 76), (84, 90), (40, 94)]))
            html("<div class='art'>"
                 f"<img src='app/static/virus.webp' alt='Virus particle'>{squares}{pluses}"
                 f"<div class='chip' style='left:0;top:0'>▪ &gt; OUTBREAK_SIM<br>▪ <i>DAY "
                 f"{total_days:02d}</i></div>"
                 "<svg class='globe' width='28' height='28' viewBox='0 0 24 24' fill='none' "
                 "stroke='#0d0d0d' stroke-width='1.4'><circle cx='12' cy='12' r='10'/>"
                 "<ellipse cx='12' cy='12' rx='4.5' ry='10'/><path d='M2 12h20M4 7h16M4 17h16'/>"
                 "</svg>"
                 f"<div class='coords'>NODES_ {pop.n}<br>EDGES_ {len(pop.edges())}<br>"
                 f"SOURCES_ {len(pop.sources)}</div>"
                 "<div class='scn'>//SCN_00</div></div>")
    st.stop()

# ---------------------------------------------------------------------------
# Navbar (inner pages only)
# ---------------------------------------------------------------------------

with st.container(key="nav"):
    # empty outer columns keep the three links in the centre
    cols = st.columns([3, 1.5, 1.5, 1.5, 3], vertical_alignment="center")
    for col, key in zip(cols[1:4], PAGES):
        col.button(PAGES[key], key=f"go_{key}", on_click=go_to, args=(key,),
                   type="primary" if key == page else "tertiary")

# ---------------------------------------------------------------------------
# Page: Spread (configuration + multi-source BFS)
# ---------------------------------------------------------------------------

if page == "spread":
    with st.container(key="panel_cfg"):
        section(1, "Configure population")
        a, b, c = st.columns([4, 2, 1.6], vertical_alignment="bottom", gap="large")
        a.slider("People in the population", 20, 80, step=5, key="n")
        b.slider("Initially infected", 1, 5, key="src")
        c.button("NEW LAYOUT", key="relayout", type="secondary", width="stretch",
                 on_click=lambda: st.session_state.update(seed=st.session_state.seed + 1))

    with st.container(key="panel_spread"):
        section(2, "Multi-source BFS")
        g, s = st.columns([3, 2], gap="large")
        with s:
            status_panel("System status", [
                ("POPULATION", None, f"{pop.n}", False),
                ("INITIALLY INFECTED", len(pop.sources) / pop.n, f"{len(pop.sources)}", False),
                ("INFECTED", infected / pop.n, f"{infected} / {pop.n}", False),
                ("OUTBREAK LENGTH", None, f"{total_days} DAYS", False),
            ], banner=f"WHOLE POPULATION INFECTED BY DAY {total_days}")
            st.write("")
            shown = st.slider("Replay day", 0, total_days, total_days)
            st.plotly_chart(curve_figure([("Infected", infected_per_day(day, total_days))],
                                         height=250), width="stretch", theme=None,
                            config=PLOT_CONFIG)
        with g:
            st.plotly_chart(grid_figure(pop, day, upto=shown, height=540), width="stretch",
                            theme=None, config=PLOT_CONFIG)
            grid_legend()
    st.write("")
    with st.expander("How multi-source BFS works"):
        st.code("""queue ← all initially infected people, day = 0
while queue not empty:
    u ← queue.pop_front()
    for each neighbour v of u:
        if v is healthy:
            day[v] ← day[u] + 1      # infected the next day
            queue.push_back(v)
answer = max(day)                   # days until everyone is infected""", language="text")
        st.markdown("All sources start in the queue together, so each person is reached "
                    "from the *nearest* infected person. Time **O(V + E)**, space **O(V)**.")

# ---------------------------------------------------------------------------
# Page: Mutation (variant tree + parent comparison)
# ---------------------------------------------------------------------------

elif page == "mutation":
    variants = evolve(total_days, every=MUTATION_EVERY, seed=st.session_state.seed)

    # which node is selected: last click on the tree, else the newest variant
    clicked = (st.session_state.get("tree") or {}).get("selection", {}).get("points", [])
    if clicked:
        point = clicked[0]
        if "customdata" in point:
            st.session_state.variant = int(point["customdata"])
        elif point.get("curve_number") == 2:                 # the node trace
            st.session_state.variant = int(point["point_index"])
    sel = st.session_state.get("variant", len(variants) - 1)
    if not 0 <= sel < len(variants):
        sel = len(variants) - 1
    v = variants[sel]

    with st.container(key="panel_tree"):
        section(1, "Variant family tree")
        html(f"<div class='hint' style='margin-bottom:1rem'>EVERY {MUTATION_EVERY} DAYS THE "
             f"NEWEST VARIANTS MUTATE INTO ONE OR TWO CHILDREN. {len(variants)} VARIANTS OVER "
             f"{total_days} DAYS. <b style='color:#0d0d0d'>CLICK A NODE</b> TO COMPARE IT WITH "
             f"ITS PARENT.</div>")
        t, d = st.columns([1, 1], gap="large")
        with t:
            st.plotly_chart(tree_figure(variants, selected=sel), key="tree", on_select="rerun",
                            selection_mode="points", width="stretch", theme=None,
                            config=PLOT_CONFIG)
            html("<div class='legend'>"
                 "<span><span class='sw' style='background:#0d0d0d'></span>ORIGINAL (V0)</span>"
                 "<span><span class='sw' style='background:#6d28d9'></span>SELECTED</span>"
                 "<span><span class='sw' style='background:#d4f53c'></span>NEWEST (LEAF)</span>"
                 "<span>ED = EDIT DISTANCE TO PARENT</span></div>")
        with d:
            path, x = [], v.vid
            while x != -1:
                path.append(variants[x].name)
                x = variants[x].parent
            html(f"<div class='h2'>{v.name} · DAY {v.day}</div>"
                 f"<div class='lineage'>LINEAGE &nbsp;{' → '.join(reversed(path[1:]))}"
                 f"{' → ' if len(path) > 1 else ''}<b>{path[0]}</b></div>")
            if v.parent < 0:
                html("<div class='seq'><span class='tag'>V0</span>"
                     + "".join(f"<span>{ch}</span>" for ch in v.genome) + "</div>")
                html("<div class='hint' style='margin-top:1rem'>THE ORIGINAL VIRUS HAS NO "
                     "PARENT. CLICK ANOTHER NODE TO SEE HOW IT CHANGED.</div>")
            else:
                p = variants[v.parent]
                lcs, similarity, dist = compare(p, v)
                html(alignment_html(p.genome, v.genome, p.name, v.name))
                st.write("")
                status_panel(None, [
                    ("LCS LENGTH", lcs / max(len(p.genome), len(v.genome)), f"{lcs}", False),
                    ("SIMILARITY", similarity, f"{100 * similarity:.0f}%", False),
                    ("EDIT DISTANCE", None, f"{dist}", False),
                ], banner=describe_changes(p.genome, v.genome) or "NO CHANGE")
                html("<div class='legend'>"
                     "<span><span class='sw' style='background:#6d28d9'></span>CHANGED</span>"
                     "<span><span class='sw' style='background:#d4f53c'></span>INSERTED</span>"
                     "<span><span class='sw' style='background:#0d0d0d'></span>DELETED</span>"
                     "</div>")
    st.write("")
    with st.expander(f"All {len(variants)} variants"):
        for x in variants:
            if x.parent < 0:
                body = "<div class='seq'>" + "".join(f"<span>{ch}</span>" for ch in x.genome)
                html(f"<div class='card'><div class='card-top'><span><span class='num'>"
                     f"/{x.name}</span>ORIGINAL</span><span>DAY {x.day:02d}</span></div>"
                     f"{body}</div></div>")
                continue
            p = variants[x.parent]
            lcs, similarity, dist = compare(p, x)
            html(f"<div class='card'><div class='card-top'><span><span class='num'>/{x.name}"
                 f"</span>FROM {p.name}</span><span>DAY {x.day:02d}</span></div>"
                 f"{alignment_html(p.genome, x.genome, p.name, x.name)}<div class='stats'>"
                 f"<span>LCS <b>{lcs}</b></span><span>SIMILARITY <b>{100 * similarity:.0f}%"
                 f"</b></span><span>EDIT DISTANCE <b>{dist}</b></span>"
                 f"<span>{describe_changes(p.genome, x.genome)}</span></div></div>")
    with st.expander("How LCS and Edit Distance work"):
        st.code("""LCS:   dp[i][j] = dp[i-1][j-1] + 1               if A[i] = B[j]
              = max(dp[i-1][j], dp[i][j-1])       otherwise
       similarity = LCS / max(len A, len B)

Edit:  dp[i][j] = dp[i-1][j-1]                   if A[i] = B[j]
              = 1 + min(dp[i-1][j],     delete
                        dp[i][j-1],     insert
                        dp[i-1][j-1])   substitute""", language="text")
        st.markdown("Both fill an (n+1) × (m+1) table: time **O(n·m)**, space **O(n·m)**.")

# ---------------------------------------------------------------------------
# Page: Isolation (backtracking)
# ---------------------------------------------------------------------------

else:
    candidates = pop.n - len(pop.sources)
    with st.container(key="panel_iso_cfg"):
        section(1, "Backtracking isolation")
        a, b = st.columns([5, 1.2], vertical_alignment="bottom", gap="large")
        a.slider("People to isolate", 1, 4, key="k")
        run = b.button("FIND BEST ↗", key="find", type="primary", width="stretch")
        k = st.session_state.k
        combos = math.comb(candidates, k)
        html(f"<div class='hint'>BACKTRACKING TRIES EVERY GROUP OF UP TO {k} PEOPLE "
             f"({combos:,} GROUPS OF EXACTLY {k}), RE-RUNS THE BFS FOR EACH AND KEEPS THE "
             f"GROUP THAT LEAVES THE FEWEST PEOPLE INFECTED. POPULATION AND INITIALLY "
             f"INFECTED ARE SET ON THE SPREAD PAGE.</div>")
        if combos > 300_000:
            st.warning("Large search: this may take up to a minute. A smaller population or "
                       "fewer people to isolate is faster.")

    key = (st.session_state.n, st.session_state.src, st.session_state.seed, k)
    results = st.session_state.setdefault("results", {})
    if run:
        with st.spinner("Backtracking…"):
            results[key] = best_isolation(pop.adj, pop.sources, k)

    with st.container(key="panel_iso_res"):
        if key in results:
            isolated, after, after_days, stats = results[key]
            new_day = multi_source_bfs(pop.adj, pop.sources, isolated)
            section(2, "Outbreak comparison")
            s, c = st.columns([2, 3], gap="large")
            with s:
                status_panel("Before vs after", [
                    ("INFECTED BEFORE", infected / pop.n, f"{infected}", True),
                    ("INFECTED AFTER", after / pop.n, f"{after}", False),
                    ("REDUCTION", (infected - after) / infected,
                     f"{100 * (infected - after) / infected:.0f}%", False),
                    ("OUTBREAK ENDS", None, f"DAY {after_days} (WAS {total_days})", False),
                ], banner="ISOLATE " + " · ".join(f"P{v}" for v in sorted(isolated)))
                note = (f"CHECKED {stats['sets_checked']:,} GROUPS IN {stats['seconds']:.2f} S · "
                        f"SKIPPED {stats['skipped']:,} BRANCHES WITH PEOPLE ALREADY CUT OFF.")
                if not stats["complete"]:
                    note += " STOPPED AT THE 60 S LIMIT: BEST GROUP FOUND SO FAR."
                html(f"<div class='hint' style='margin-top:1rem'>{note}</div>")
            with c:
                horizon = max(total_days, after_days)
                st.plotly_chart(curve_figure(
                    [("Without isolation", infected_per_day(day, horizon)),
                     ("With isolation", infected_per_day(new_day, horizon))], height=320),
                    width="stretch", theme=None, config=PLOT_CONFIG)
            st.write("")
            g1, g2 = st.columns(2, gap="large")
            with g1:
                html(f"<div class='sec'><span class='num'>A</span>Without isolation · "
                     f"{infected} infected</div>")
                st.plotly_chart(grid_figure(pop, day, height=430), width="stretch",
                                theme=None, config=PLOT_CONFIG, key="before")
            with g2:
                saved = [v for v in range(pop.n) if day[v] >= 0 and new_day[v] == -1
                         and v not in isolated]
                html(f"<div class='sec'><span class='num'>B</span>With isolation · "
                     f"{after} infected · {len(saved)} saved</div>")
                st.plotly_chart(grid_figure(pop, new_day, isolated=isolated, saved=saved,
                                            height=430),
                                width="stretch", theme=None, config=PLOT_CONFIG, key="after")
            grid_legend(saved=True)
        else:
            section(2, "Population before isolation")
            st.plotly_chart(grid_figure(pop, day, height=470), width="stretch", theme=None,
                            config=PLOT_CONFIG, key="preview")
            grid_legend()
    st.write("")
    with st.expander("How the backtracking works"):
        st.code("""backtrack(start, chosen):
    run BFS with `chosen` isolated; keep it if fewest infected so far
    if |chosen| = K: return
    for i in start .. n-1:
        if candidate[i] can still be infected:   # cut-off people are pointless
            chosen.push(candidate[i])
            backtrack(i + 1, chosen)
            chosen.pop()                         # undo and try the next one""",
                language="text")
        st.markdown("Ties are broken by the later outbreak end. Initially infected people "
                    "cannot be isolated. Time **O(C(V, K) · (V + E))**, which grows very "
                    "quickly with K.")
