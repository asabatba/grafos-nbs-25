#!/usr/bin/env python3
"""
Graph Recommender (NetworkX) — 45‑min class demo

What this script shows:
  1) Build a bipartite user–item graph from interactions
  2) Two graph-based recommenders:
       a) User–User Jaccard CF
       b) Personalized PageRank on the bipartite graph
  3) Simple hold‑out evaluation (last item per user) with Precision@K / Recall@K

Usage:
  python graph_recsys_networkx.py --csv interactions.csv --user u01 --k 10
Requires:
  pip install networkx pandas matplotlib
"""

import argparse
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def load_interactions(path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df


def build_bipartite_graph(df):
    # df columns: user, item, timestamp
    B = nx.Graph()
    users = df["user"].unique()
    items = df["item"].unique()
    B.add_nodes_from(users, bipartite="users")
    B.add_nodes_from(items, bipartite="items")
    # Add edges with timestamp as attribute (last interaction wins)
    for row in df.itertuples(index=False):
        B.add_edge(row.user, row.item, timestamp=row.timestamp)
    return B


def train_test_split_last_item_per_user(df):
    """Hold out the last interaction per user as test, the rest as train."""
    df_sorted = df.sort_values(["user", "timestamp"])
    last_idx = df_sorted.groupby("user").tail(1).index
    test = df_sorted.loc[last_idx]
    train = df_sorted.drop(last_idx)
    return train, test


def to_user_items(df):
    user_items = defaultdict(set)
    for row in df.itertuples(index=False):
        user_items[row.user].add(row.item)
    return user_items


def jaccard_user_sim(user_items):
    """Jaccard similarity between users based on their item sets."""
    users = list(user_items.keys())
    sim = defaultdict(dict)
    for i, u in enumerate(users):
        Ui = user_items[u]
        for v in users[i + 1 :]:
            Uj = user_items[v]
            inter = len(Ui & Uj)
            if inter == 0:
                continue
            union = len(Ui | Uj)
            s = inter / union
            sim[u][v] = s
            sim[v][u] = s
    return sim


def recommend_cf(user, user_items, sim, k_neighbors=10, topn=10):
    """Score candidate items using weighted sum of neighbor similarities."""
    seen = user_items.get(user, set())
    # sort neighbors by similarity
    neigh = sorted(sim.get(user, {}).items(), key=lambda x: x[1], reverse=True)[
        :k_neighbors
    ]
    scores = defaultdict(float)
    for v, w in neigh:
        for it in user_items[v]:
            if it not in seen:
                scores[it] += w
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:topn]
    return [it for it, _ in ranked]


def recommend_ppr(B, user, topn=10, alpha=0.85, max_iter=100):
    """Personalized PageRank from a given user node on the bipartite graph."""
    if user not in B:
        return []
    pr = nx.pagerank(B, alpha=alpha, personalization={user: 1.0}, max_iter=max_iter)
    # Recommend highest‑ranked items the user hasn't seen
    seen = set(B.neighbors(user))
    candidates = [
        (n, s)
        for n, s in pr.items()
        if B.nodes[n].get("bipartite") == "items" and n not in seen
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)
    return [n for n, _ in candidates[:topn]]


def precision_recall_at_k(recs, truth, k=10):
    recs_k = recs[:k]
    hit = len(set(recs_k) & set(truth))
    prec = hit / max(1, len(recs_k))
    rec = hit / max(1, len(truth))
    return prec, rec


def evaluate(train_df, test_df, method, B=None, k_neighbors=10, topn=10):
    train_ui = to_user_items(train_df)
    test_ui = to_user_items(test_df)
    users = [u for u in train_ui.keys() if u in test_ui and len(test_ui[u]) > 0]
    results = []
    if method == "cf":
        sim = jaccard_user_sim(train_ui)
        for u in users:
            recs = recommend_cf(u, train_ui, sim, k_neighbors=k_neighbors, topn=topn)
            prec, rec = precision_recall_at_k(recs, list(test_ui[u]), k=topn)
            results.append((prec, rec))
    elif method == "ppr":
        assert B is not None, "Bipartite graph B is required for PPR method"
        for u in users:
            recs = recommend_ppr(B, u, topn=topn)
            prec, rec = precision_recall_at_k(recs, list(test_ui[u]), k=topn)
            results.append((prec, rec))
    else:
        raise ValueError("Unknown method")
    if results:
        prec_avg = sum(p for p, _ in results) / len(results)
        rec_avg = sum(r for _, r in results) / len(results)
    else:
        prec_avg, rec_avg = 0.0, 0.0
    return prec_avg, rec_avg, len(results)


def plot_ego(B, user, max_neighbors=12):
    """Optional small visualization for the teaching demo."""
    if user not in B:
        print(f"{user} not in graph")
        return
    # build tiny ego graph (user + items + other users for first few items)
    items = list(B.neighbors(user))[:max_neighbors]
    nodes = set([user]) | set(items)
    for it in items:
        nodes |= set(list(B.neighbors(it))[:6])
    H = B.subgraph(nodes).copy()
    pos = nx.spring_layout(H, seed=7)
    nx.draw(H, pos, with_labels=True, node_size=600, font_size=8)
    plt.title(f"Ego graph around {user}")
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="interactions.csv")
    ap.add_argument("--user", default="u01")
    ap.add_argument("--k", type=int, default=10, help="Top‑K recommendations")
    ap.add_argument("--neighbors", type=int, default=10, help="CF: K nearest users")
    ap.add_argument("--plot", action="store_true", help="Show a small ego‑graph plot")
    args = ap.parse_args()

    df = load_interactions(args.csv)
    B = build_bipartite_graph(df)
    train, test = train_test_split_last_item_per_user(df)

    # --- CF ---
    prec, rec, n = evaluate(
        train, test, method="cf", k_neighbors=args.neighbors, topn=args.k
    )
    print(
        f"[CF] users evaluated={n}  Precision@{args.k}={prec:.3f}  Recall@{args.k}={rec:.3f}"
    )

    # --- PPR ---
    B_train = build_bipartite_graph(train)
    prec2, rec2, n2 = evaluate(train, test, method="ppr", B=B_train, topn=args.k)
    print(
        f"[PPR] users evaluated={n2} Precision@{args.k}={prec2:.3f} Recall@{args.k}={rec2:.3f}"
    )

    # Show example recommendations for the chosen user
    train_ui = to_user_items(train)
    sim = jaccard_user_sim(train_ui)
    cf_recs = recommend_cf(
        args.user, train_ui, sim, k_neighbors=args.neighbors, topn=args.k
    )
    ppr_recs = recommend_ppr(B_train, args.user, topn=args.k)

    print(f"\nUser {args.user} — CF top{args.k}:  {cf_recs}")
    print(f"User {args.user} — PPR top{args.k}: {ppr_recs}")

    if args.plot:
        plot_ego(B_train, args.user)


if __name__ == "__main__":
    main()
