"""
Checks the hand-written algorithms against simple independent references.

Run:  python tests/test_algorithms.py
"""

import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.backtracking import best_isolation
from algorithms.bfs import multi_source_bfs, outbreak_summary
from algorithms.edit_distance import edit_distance, edit_operations
from algorithms.lcs import lcs_length, lcs_string
from simulation.population import generate_population


def _is_subsequence(s, t):
    it = iter(t)
    return all(c in it for c in s)


def test_bfs_days_are_nearest_source_distances():
    """BFS day = shortest grid-path length to the nearest source (checked
    with a slow Bellman-Ford style relaxation)."""
    pop = generate_population(60, seed=3)
    day = multi_source_bfs(pop.adj, pop.sources)
    dist = [0 if v in pop.sources else float("inf") for v in range(pop.n)]
    for _ in range(pop.n):
        for u in range(pop.n):
            for v in pop.adj[u]:
                dist[v] = min(dist[v], dist[u] + 1)
    assert day == dist
    assert outbreak_summary(day) == (pop.n, max(dist))       # graph is connected


def test_lcs_and_edit_distance():
    assert lcs_length("ACGTACGT", "ACGTTGGT") == 6
    assert edit_distance("kitten", "sitting") == 3
    rng = random.Random(0)
    for _ in range(200):
        a = "".join(rng.choice("ACGT") for _ in range(rng.randint(1, 8)))
        b = "".join(rng.choice("ACGT") for _ in range(rng.randint(1, 8)))
        s = lcs_string(a, b)
        assert len(s) == lcs_length(a, b) and _is_subsequence(s, a) and _is_subsequence(s, b)
        ops = edit_operations(a, b)
        assert sum(op != "match" for op, _, _ in ops) == edit_distance(a, b)


def test_backtracking_matches_brute_force():
    for seed in range(5):
        pop = generate_population(25, seed=seed)
        cand = [v for v in range(pop.n) if v not in pop.sources]
        for k in (1, 2, 3):
            _, infected, days, _ = best_isolation(pop.adj, pop.sources, k)
            brute = min((outbreak_summary(multi_source_bfs(pop.adj, pop.sources, c))[0],
                         -outbreak_summary(multi_source_bfs(pop.adj, pop.sources, c))[1])
                        for c in itertools.combinations(cand, k))
            assert (infected, -days) == brute, (seed, k)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
