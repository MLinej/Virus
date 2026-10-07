"""
Draws the population grid with Plotly.

"+" marks are empty positions. Squares are people, and thin lines
connect neighbours (the graph edges). The number in an infected square
is the day that person was infected, which is their BFS level.

Colours: black = initially infected, red = infected later, light gray =
healthy, green = saved by the isolation, gray x = isolated.
"""

import plotly.graph_objects as go

INK = "#0d0d0d"
PURPLE = "#6d28d9"
LIME = "#d4f53c"
MUTED = "#a3a39e"
RED = "#e03131"
GREEN = "#2f9e44"
HEALTHY = "#d9d9d4"
EMPTY = "rgba(13,13,13,0.22)"
EDGE = "rgba(13,13,13,0.28)"
FONT = "JetBrains Mono, ui-monospace, monospace"


def grid_figure(pop, day, upto=None, isolated=(), saved=(), height=480):
    """day[v] = infection day (-1 never). People with day <= upto are infected.
    `saved` = people who would have been infected without the isolation."""
    upto = max(day) if upto is None else upto
    isolated = set(isolated)
    sources = set(pop.sources)
    saved = set(saved)
    fig = go.Figure()

    taken = set(pop.cells)
    empty = [(r, c) for r in range(pop.size) for c in range(pop.size) if (r, c) not in taken]
    fig.add_trace(go.Scatter(x=[c for _, c in empty], y=[r for r, _ in empty], mode="markers",
                             marker=dict(size=7, symbol="cross-thin",
                                         line=dict(width=1, color=EMPTY)),
                             hoverinfo="skip"))

    xs, ys = [], []
    for u, v in pop.edges():
        if u in isolated or v in isolated:
            continue
        (r1, c1), (r2, c2) = pop.cells[u], pop.cells[v]
        xs += [c1, c2, None]
        ys += [r1, r2, None]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=EDGE, width=1.5),
                             hoverinfo="skip"))

    colors, symbols, labels, text_colors, hover = [], [], [], [], []
    for v in range(pop.n):
        if v in isolated:
            colors.append(MUTED); symbols.append("x-thin-open"); labels.append("")
            hover.append(f"PERSON {v} · ISOLATED")
        elif 0 <= day[v] <= upto:
            colors.append(INK if v in sources else RED); symbols.append("square")
            labels.append(str(day[v]))
            hover.append(f"PERSON {v} · {'INITIALLY INFECTED' if v in sources else f'INFECTED DAY {day[v]}'}")
        elif v in saved:
            colors.append(GREEN); symbols.append("square"); labels.append("")
            hover.append(f"PERSON {v} · SAVED BY ISOLATION")
        else:
            colors.append(HEALTHY); symbols.append("square"); labels.append("")
            hover.append(f"PERSON {v} · HEALTHY")
        text_colors.append("#ffffff")

    fig.add_trace(go.Scatter(
        x=[c for _, c in pop.cells], y=[r for r, _ in pop.cells], mode="markers+text",
        text=labels, textfont=dict(color=text_colors, size=11, family=FONT),
        hovertext=hover, hoverinfo="text",
        marker=dict(size=24, color=colors, symbol=symbols,
                    line=dict(width=[2.5 if v in isolated else 0 for v in range(pop.n)],
                              color=MUTED))))

    fig.update_layout(height=height, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT), hoverlabel=dict(font_family=FONT),
                      xaxis=dict(visible=False, range=[-0.7, pop.size - 0.3]),
                      yaxis=dict(visible=False, autorange="reversed", scaleanchor="x"))
    return fig


def curve_figure(series, height=260):
    """series: list of (label, cumulative infected per day)."""
    styles = [(PURPLE, "solid"), (INK, "dash")]
    fig = go.Figure()
    for i, (label, values) in enumerate(series):
        color, dash = styles[i % 2]
        fig.add_trace(go.Scatter(x=list(range(len(values))), y=values, name=label.upper(),
                                 mode="lines+markers",
                                 marker=dict(size=7, symbol="square", color=color),
                                 line=dict(width=2, color=color, dash=dash)))
    fig.update_layout(height=height, margin=dict(l=48, r=8, t=36, b=44), hovermode="x unified",
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT, size=13, color=INK),
                      xaxis_title="DAY", yaxis_title="INFECTED",
                      showlegend=len(series) > 1,
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0,
                                  entrywidth=210, font=dict(size=12)))
    fig.update_xaxes(showgrid=False, dtick=1, linecolor="rgba(13,13,13,0.35)")
    fig.update_yaxes(gridcolor="rgba(13,13,13,0.08)", zeroline=False)
    return fig
