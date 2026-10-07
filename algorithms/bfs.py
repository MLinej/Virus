"""
Multi-source Breadth-First Search.

All initially infected people go into the queue at day 0. Each BFS level
is one day: every infected person infects all healthy neighbours on the
next day. The BFS distance of a person is therefore the day they get
infected, and the largest distance is the number of days until the
whole (reachable) population is infected.

Time  O(V + E): every person is queued once, and every contact is
scanned once.
Space O(V).
"""

from collections import deque


def multi_source_bfs(adj, sources, isolated=()):
    """Returns day[v], the day person v is infected (-1 = never)."""
    isolated = set(isolated)
    day = [-1] * len(adj)
    queue = deque()
    for s in sources:                       # all sources start together
        day[s] = 0
        queue.append(s)

    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if day[v] == -1 and v not in isolated:
                day[v] = day[u] + 1         # infected one day after u
                queue.append(v)
    return day


def outbreak_summary(day):
    """(people infected, days until nobody new gets infected)."""
    infected = [d for d in day if d >= 0]
    return len(infected), max(infected, default=0)


def infected_per_day(day, last_day):
    """Cumulative number of infected people at the end of each day."""
    counts = [0] * (last_day + 1)
    for d in day:
        if 0 <= d <= last_day:
            counts[d] += 1
    total, out = 0, []
    for c in counts:
        total += c
        out.append(total)
    return out
