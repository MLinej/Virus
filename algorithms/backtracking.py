"""
Backtracking: which K people should be isolated?

Every set of at most K people (initially infected people excluded) is a
possible answer. For each set, the multi-source BFS is run again with
those people isolated, and the set is scored by

    1. fewest people infected        (main goal)
    2. most days until the outbreak ends   (tie-break: slower is better)

Subsets are built in increasing index order, so each one is generated
exactly once:

    backtrack(start, chosen):
        run BFS with `chosen` isolated, keep it if it is the best so far
        if |chosen| == K: return
        for i in start .. n-1:
            if candidate[i] can still be infected:   # otherwise pointless
                chosen.push(candidate[i])
                backtrack(i + 1, chosen)
                chosen.pop()                         # undo = backtrack

Pruning: if the virus can no longer reach a person (they are already cut
off by `chosen`), isolating them changes nothing, so that branch is
skipped. Isolating more people can only shrink the infected region, so
this never loses the best answer.

Time  O(C(V, K) * (V + E)) in the worst case.
Space O(V) for the BFS, plus O(K) for the recursion.
"""

import math
import time

from algorithms.bfs import multi_source_bfs, outbreak_summary


def best_isolation(adj, sources, k, time_limit=60.0):
    source_set = set(sources)
    candidates = [v for v in range(len(adj)) if v not in source_set]
    best = {"isolated": [], "key": None, "infected": 0, "days": 0}
    stats = {"sets_checked": 0, "skipped": 0, "complete": True,
             "all_combinations": math.comb(len(candidates), min(k, len(candidates)))}
    chosen = []
    start_time = time.perf_counter()

    def backtrack(start):
        if time.perf_counter() - start_time > time_limit:
            stats["complete"] = False
            return

        day = multi_source_bfs(adj, sources, chosen)
        infected, days = outbreak_summary(day)
        stats["sets_checked"] += 1
        key = (infected, -days)
        if best["key"] is None or key < best["key"]:
            best.update(isolated=list(chosen), key=key, infected=infected, days=days)

        if len(chosen) == k:
            return
        for i in range(start, len(candidates)):
            v = candidates[i]
            if day[v] == -1:                 # already cut off: no effect
                stats["skipped"] += 1
                continue
            chosen.append(v)
            backtrack(i + 1)
            chosen.pop()

    backtrack(0)
    stats["seconds"] = time.perf_counter() - start_time
    return best["isolated"], best["infected"], best["days"], stats
