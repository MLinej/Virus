"""
Population graph on a 2-D grid.

Some grid positions hold a person and some are empty. Two people are in
contact (an edge) when they stand in neighbouring cells: up, down, left
or right.

People are placed by random growth from the centre, so everyone is
connected. Cells with few occupied neighbours are preferred, which gives
a branchy shape with narrow corridors. Isolating one person at a
corridor can then shield a whole region, which is what makes the
backtracking page interesting.
"""

import math
import random
from dataclasses import dataclass

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


@dataclass
class Population:
    size: int          # grid is size x size
    cells: list        # cells[v] = (row, col) of person v
    adj: list          # adj[v] = list of neighbouring people
    sources: list      # initially infected people

    @property
    def n(self):
        return len(self.cells)

    def edges(self):
        return [(u, v) for u in range(self.n) for v in self.adj[u] if u < v]


def generate_population(n, seed=0, sources=3):
    rng = random.Random(seed)
    size = math.ceil(math.sqrt(n / 0.5))           # about half the grid is empty
    start = (size // 2, size // 2)
    occupied = {start}
    order = [start]

    def inside(r, c):
        return 0 <= r < size and 0 <= c < size

    def occupied_neighbours(cell):
        return sum((cell[0] + dr, cell[1] + dc) in occupied for dr, dc in DIRECTIONS)

    while len(order) < n:
        frontier = {(r + dr, c + dc) for r, c in occupied for dr, dc in DIRECTIONS
                    if inside(r + dr, c + dc) and (r + dr, c + dc) not in occupied}
        frontier = sorted(frontier)
        weights = [1 / occupied_neighbours(cell) ** 3 for cell in frontier]
        cell = rng.choices(frontier, weights)[0]
        occupied.add(cell)
        order.append(cell)

    index = {cell: v for v, cell in enumerate(order)}
    adj = [[index[(r + dr, c + dc)] for dr, dc in DIRECTIONS if (r + dr, c + dc) in index]
           for r, c in order]
    return Population(size=size, cells=order, adj=adj,
                      sources=pick_sources(order, adj, sources, rng))


def pick_sources(cells, adj, count, rng):
    """Initially infected people: well-connected and spread apart, so the
    outbreak cannot be stopped by simply fencing in one corner."""
    pool = [v for v in range(len(cells)) if len(adj[v]) >= 3] or list(range(len(cells)))
    chosen = [rng.choice(pool)]
    while len(chosen) < min(count, len(pool)):
        # farthest-point choice (Manhattan distance on the grid)
        far = max((v for v in pool if v not in chosen),
                  key=lambda v: min(abs(cells[v][0] - cells[s][0]) +
                                    abs(cells[v][1] - cells[s][1]) for s in chosen))
        chosen.append(far)
    return sorted(chosen)
