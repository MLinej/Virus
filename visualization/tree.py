"""
Draws the variant family tree with Plotly.

Layout: a depth-first walk gives every leaf the next free x position,
and each parent sits centred above its children. y = generation, so
each row is one mutation day. Each edge is labelled with the edit
distance between parent and child.
"""

import plotly.graph_objects as go

from algorithms.edit_distance import edit_distance
from visualization.grid import FONT, INK, LIME, PURPLE

PANEL = "#f7f7f4"


def tree_layout(variants):
    pos, next_x = {}, [0]

    def place(vid):
        v = variants[vid]
        if not v.children:
            x = next_x[0]
            next_x[0] += 1
        else:
            xs = [place(c) for c in v.children]
            x = (xs[0] + xs[-1]) / 2
        pos[vid] = (x, v.generation)
        return x

    place(0)
    return pos


def tree_figure(variants, selected=None, height=460):
    pos = tree_layout(variants)
    fig = go.Figure()

    # elbow edges parent → child
    xs, ys, lx, ly, lt = [], [], [], [], []
    for v in variants[1:]:
        (x0, y0), (x1, y1) = pos[v.parent], pos[v.vid]
        mid = (y0 + y1) / 2
        xs += [x0, x0, x1, x1, None]
        ys += [y0, mid, mid, y1, None]
        lx.append(x1 + 0.06)
        ly.append((mid + y1) / 2)
        lt.append(f"ED {edit_distance(variants[v.parent].genome, v.genome)}")
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", hoverinfo="skip",
                             line=dict(color="rgba(13,13,13,0.45)", width=1.5)))
    fig.add_trace(go.Scatter(x=lx, y=ly, mode="text", text=lt, hoverinfo="skip",
                             textposition="middle right",
                             textfont=dict(family=FONT, size=11, color=PURPLE)))

    # nodes
    fills, texts, hover = [], [], []
    for v in variants:
        if v.vid == selected:
            fills.append(PURPLE); texts.append("#ffffff")
        elif v.vid == 0:
            fills.append(INK); texts.append("#ffffff")
        elif not v.children:
            fills.append(LIME); texts.append(INK)
        else:
            fills.append(PANEL); texts.append(INK)
        parent = "—" if v.parent < 0 else variants[v.parent].name
        hover.append(f"<b>{v.name}</b> · DAY {v.day}<br>PARENT {parent}<br>{v.genome}")
    fig.add_trace(go.Scatter(
        x=[pos[v.vid][0] for v in variants], y=[pos[v.vid][1] for v in variants],
        mode="markers+text", text=[v.name for v in variants],
        textfont=dict(family=FONT, size=12, color=texts), customdata=[v.vid for v in variants],
        hovertext=hover, hoverinfo="text",
        marker=dict(symbol="square", size=40, color=fills, line=dict(width=1.5, color=INK)),
        selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1))))

    depth = max(v.generation for v in variants)
    days = {v.generation: v.day for v in variants}
    width = max(p[0] for p in pos.values())
    fig.update_layout(
        height=height, showlegend=False, dragmode=False, clickmode="event+select",
        margin=dict(l=70, r=20, t=20, b=20), plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT, size=12, color=INK),
        hoverlabel=dict(font_family=FONT),
        xaxis=dict(visible=False, range=[-0.7, width + 0.7]),
        yaxis=dict(tickvals=list(range(depth + 1)),
                   ticktext=[f"DAY {days[g]}" for g in range(depth + 1)],
                   gridcolor="rgba(13,13,13,0.08)", zeroline=False,
                   range=[depth + 0.6, -0.6]))
    return fig
