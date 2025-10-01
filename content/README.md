
# 45‑Minute Session: Graph Recommenders with NetworkX

## Quickstart
```bash
python -V  # 3.9+ recommended
pip install networkx pandas matplotlib
python graph_recsys_networkx.py --csv interactions.csv --user u01 --k 10 --neighbors 10 --plot
```

## What the demo covers
- Building a bipartite user–item graph from `interactions.csv`
- Two recommenders:
  - **User–User Jaccard CF** (on item sets)
  - **Personalized PageRank** on the bipartite graph
- Hold‑out evaluation (last item per user) with Precision@K / Recall@K
- Small ego‑graph visualization

## Suggested 45‑min agenda
1. (0–5) Why graphs for recommendations? Nodes/edges, bipartite structure, two‑hop paths.
2. (5–10) Framing as **link prediction** / **ranking**; cold‑start & graph advantages.
3. (10–22) Live code: build the graph, show ego‑graph, explain attributes.
4. (22–34) Implement CF (Jaccard) + PPR; generate top‑K for a sample user.
5. (34–41) Quick evaluation (Precision@K & Recall@K); compare CF vs PPR.
6. (41–45) Wrap‑up: trade‑offs, scaling beyond NetworkX, Q&A.

## Files
- `interactions.csv` — synthetic user–item interactions with timestamps
- `graph_recsys_networkx.py` — the full demo
