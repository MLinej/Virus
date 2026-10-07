"""
Virus mutation over time, as a parent → child tree.

The original virus has a random genome over {A, C, G, T}. Every few days
of the outbreak, each of the newest variants mutates into one or two
children: 1–2 point changes (mostly substitutions, sometimes an
insertion or a deletion). This gives a family tree of variants. Each
variant is compared with its parent using LCS and Edit Distance.
"""

import random
from dataclasses import dataclass, field

BASES = "ACGT"


@dataclass
class Variant:
    vid: int
    name: str
    day: int                   # day the variant appears
    genome: str
    parent: int                # id of the parent variant (-1 for the original)
    generation: int
    children: list = field(default_factory=list)


def mutate(genome, rng):
    g = list(genome)
    for _ in range(rng.choice([1, 1, 2])):
        pos = rng.randrange(len(g))
        r = rng.random()
        if r < 0.8:
            g[pos] = rng.choice([b for b in BASES if b != g[pos]])
        elif r < 0.9:
            g.insert(pos, rng.choice(BASES))
        else:
            del g[pos]
    return "".join(g)


def evolve(total_days, every=2, length=20, seed=0, max_variants=13, max_width=3):
    """Every `every` days, up to `max_width` of the newest variants each
    produce one or two children (at most `max_variants` in total)."""
    rng = random.Random(seed)
    variants = [Variant(0, "V0", 0, "".join(rng.choice(BASES) for _ in range(length)), -1, 0)]
    newest = [0]
    for day in range(every, total_days + 1, every):
        born = []
        for pid in newest:
            for _ in range(2 if pid == 0 else rng.choice([1, 2])):
                if len(variants) >= max_variants:
                    break
                parent = variants[pid]
                child = Variant(len(variants), f"V{len(variants)}", day,
                                mutate(parent.genome, rng), pid, parent.generation + 1)
                variants.append(child)
                parent.children.append(child.vid)
                born.append(child.vid)
        if not born:
            break
        newest = born if len(born) <= max_width else sorted(rng.sample(born, max_width))
    return variants
