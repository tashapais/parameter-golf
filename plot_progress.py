#!/usr/bin/env python3
"""Plot autoresearch progress from results.tsv — mirrors the screenshot style."""
import sys
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

TSV = "results.tsv"

def load():
    rows = []
    with open(TSV) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            try:
                rows.append({
                    "commit":      r["commit"],
                    "val_bpb":     float(r["val_bpb"]),
                    "size_mb":     float(r["size_mb"]),
                    "status":      r["status"],
                    "description": r["description"],
                })
            except (ValueError, KeyError):
                pass
    return rows

def plot(rows, out="progress.png"):
    if not rows:
        print("No data yet.")
        return

    kept   = [(i, r) for i, r in enumerate(rows) if r["status"] == "keep"]
    disc   = [(i, r) for i, r in enumerate(rows) if r["status"] != "keep"]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")

    # Discarded experiments
    if disc:
        ax.scatter([i for i, _ in disc], [r["val_bpb"] for _, r in disc],
                   color="#cccccc", s=25, zorder=2, label="Discarded")

    # Kept experiments + running best step line
    if kept:
        xs = [i for i, _ in kept]
        ys = [r["val_bpb"] for _, r in kept]

        # step line connecting kept points
        step_x, step_y = [], []
        best = None
        for i, r in enumerate(rows):
            bpb = r["val_bpb"]
            if best is None or bpb < best:
                best = bpb
            step_x.append(i)
            step_y.append(best)
        ax.step(step_x, step_y, where="post", color="#2ca02c", lw=1.5,
                zorder=3, label="Running best")

        ax.scatter(xs, ys, color="#2ca02c", s=60, zorder=4, label="Kept")

        # labels on kept points
        for i, r in kept:
            desc = r["description"][:35] + ("…" if len(r["description"]) > 35 else "")
            ax.annotate(desc, (i, r["val_bpb"]),
                        textcoords="offset points", xytext=(5, -12),
                        fontsize=6.5, color="#2ca02c", rotation=25,
                        ha="left", va="top")

    n_kept = len(kept)
    n_total = len(rows)
    ax.set_title(f"Autoresearch Progress: {n_total} Experiments, {n_kept} Kept Improvements",
                 fontsize=13)
    ax.set_xlabel("Experiment #")
    ax.set_ylabel("Validation BPB (lower is better)")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    if rows:
        bpbs = [r["val_bpb"] for r in rows]
        pad = (max(bpbs) - min(bpbs)) * 0.15 or 0.005
        ax.set_ylim(min(bpbs) - pad, max(bpbs) + pad)
    ax.set_xlim(-0.5, max(len(rows) - 0.5, 1))

    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "progress.png"
    plot(load(), out)
