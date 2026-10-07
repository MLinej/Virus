# 🦠 ViraGuard

ViraGuard simulates a virus spreading through a population graph, mutating over time, and being slowed down by isolating the right people. It is a synthetic simulation built for a Design and Analysis of Algorithms project.

## The population graph

The population is a square grid. Some positions hold a person and some are empty. Two people are in contact (an edge) when they stand next to each other: up, down, left or right. Three well-connected, spread-out people start out infected.

You choose **how many people** are in the population. **New layout** generates a different arrangement.

## Pages

The app opens on a **home page** with a short description and an image of a virus.
**Explore Spread** opens the simulation, and from then on a navbar switches between three pages.

### 1 · Spread: multi-source BFS
Here you set **how many people** are in the population and **how many are initially infected**.
**New layout** generates a different arrangement. All infected people go into the BFS queue at
day 0. Each BFS level is one day, and everyone next to an infected person gets infected the
following day. A person's BFS level is the day they get infected, and the largest level is
**the number of days until the whole population is infected**. A day slider replays the spread.

Time **O(V + E)**, space **O(V)**.

### 2 · Mutation: variant tree, LCS and Edit Distance
The virus has a genome made of A, C, G and T. Every 2 days of the outbreak, the newest variants
mutate into one or two children each (1–2 changed, inserted or deleted letters). This builds a
**family tree** of variants, drawn with parent → child edges labelled by edit distance.
Click a node to compare that variant with its **parent**:

* the two genomes aligned, with changed, inserted and deleted letters highlighted
* **LCS** (Longest Common Subsequence) and similarity = LCS / longer length
* **Edit Distance**: the minimum number of insertions, deletions and substitutions

Both are dynamic programming over an (n+1) × (m+1) table: **O(n·m)** time and space.

### 3 · Isolation: backtracking
You choose **how many people to isolate (K)**. Backtracking tries every group of up to K people (initially infected people excluded), re-runs the multi-source BFS with that group removed, and keeps the group that leaves **the fewest people infected**. Ties go to the group whose outbreak ends later. The page then compares the outbreak before and after isolation.

Branches that would isolate someone already cut off from the virus are skipped, because isolating them cannot change the result. The worst case is **O(C(V, K) · (V + E))**.

## Project structure

```
ViraGuard/
├── app.py                    the 3-page Streamlit app
├── algorithms/
│   ├── bfs.py                multi-source BFS
│   ├── lcs.py                Longest Common Subsequence (DP)
│   ├── edit_distance.py      Levenshtein Edit Distance (DP)
│   └── backtracking.py       best K people to isolate
├── simulation/
│   ├── population.py         grid population graph
│   └── mutation.py           genome and variants every few days
├── visualization/grid.py     grid drawing and infection curve (Plotly)
├── visualization/tree.py     variant family tree (Plotly)
├── static/virus.webp         hero image (served by Streamlit static serving)
├── .streamlit/config.toml    theme: light gray, black ink, purple + lime accents
└── tests/test_algorithms.py  correctness checks
```

The interface uses a "cyber-brutalist" look: a navbar with the three pages, a hero section,
square panels, monospace text (JetBrains Mono) and a condensed display font (Anton).
A page can be opened directly with `?page=spread`, `?page=mutation` or `?page=isolation`.

All algorithms are written by hand. Streamlit is used only for the UI and Plotly only for drawing.

## How to run

```bash
cd ViraGuard
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501.

To run the tests:

```bash
python tests/test_algorithms.py
```

## Image credit

The virus image is the CDC's SARS-CoV-2 illustration by Alissa Eckert, MS and Dan Higgins, MAM
(CDC Public Health Image Library #23312), which is in the public domain. It was converted to
grayscale for this project.
