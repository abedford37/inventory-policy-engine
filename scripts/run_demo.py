"""End to end: build both policies, measure realized service, plot, export."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from inventory_policy import generate, faithful_policy, improved_policy, compare
from inventory_policy.evaluate import realized_service

ASSETS = pathlib.Path(__file__).resolve().parents[1] / "assets"
BLUE, GOLD, INK = "#0055FF", "#E2AD28", "#1A1A1A"


def main():
    d = generate()
    items = d["items"]
    f = faithful_policy(items)
    im = improved_policy(items)
    tbl, fdet, imdet = compare(items, f, im)
    print("=== realized service and capital ===\n", tbl.to_string())
    below = (f["ophq_qty"] < f["min_qty"]).mean()
    print(f"\nfaithful OPHQ falls below MIN for {below:.0%} of items "
          "(OPHQ is one week of stock, MIN is a full lead time)")
    print("\nrealized service by ABC (improved):\n",
          imdet.groupby("abc")["realized"].mean().round(3).to_string())
    print("\nsafety stock share by origin (improved):\n",
          (imdet.groupby("origin")["safety_stock"].sum() / imdet["safety_stock"].sum()).round(3).to_string())

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    bins = np.linspace(0.3, 1.0, 30)
    ax[0].hist(fdet["realized"], bins=bins, color=GOLD, alpha=0.85, label="faithful formula")
    ax[0].hist(imdet["realized"], bins=bins, color=BLUE, alpha=0.75, label="improved policy")
    for t in (0.90, 0.95, 0.98):
        ax[0].axvline(t, color=INK, ls=":", lw=1)
    ax[0].set_title("Service level each policy actually delivers")
    ax[0].set_xlabel("realized cycle service level"); ax[0].set_ylabel("items")
    ax[0].legend(frameon=False); ax[0].spines[["top", "right"]].set_visible(False)

    order = ["smooth", "erratic", "intermittent", "lumpy"]
    fss = fdet.groupby("pattern")["safety_stock"].mean().reindex(order)
    iss = imdet.groupby("pattern")["safety_stock"].mean().reindex(order)
    x = np.arange(len(order))
    ax[1].bar(x - 0.2, fss, 0.4, color=GOLD, label="faithful formula")
    ax[1].bar(x + 0.2, iss, 0.4, color=BLUE, label="improved policy")
    ax[1].set_xticks(x); ax[1].set_xticklabels(order)
    ax[1].set_title("Average safety stock per item, by demand pattern")
    ax[1].set_ylabel("units"); ax[1].legend(frameon=False)
    ax[1].spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(ASSETS / "policy_comparison.png", dpi=130); plt.close()
    print("\nSaved assets/policy_comparison.png")

    # exportable outputs
    data_dir = pathlib.Path(__file__).resolve().parents[1] / "data"
    items.to_csv(data_dir / "items_sample.csv", index=False)
    d["suppliers"].to_csv(data_dir / "suppliers_sample.csv", index=False)
    out = (items[["item_id", "abc", "pattern", "origin", "supplier_id", "lead_time_days", "service_level"]]
           .merge(f.rename(columns={c: f"faithful_{c}" for c in ["min_qty", "ophq_qty", "max_qty"]})
                  [["item_id", "faithful_min_qty", "faithful_ophq_qty", "faithful_max_qty"]], on="item_id")
           .merge(im.rename(columns={c: f"improved_{c}" for c in ["min_qty", "ophq_qty", "max_qty"]})
                  [["item_id", "improved_min_qty", "improved_ophq_qty", "improved_max_qty", "safety_stock"]], on="item_id")
           .merge(fdet[["item_id", "realized"]].rename(columns={"realized": "faithful_service"}), on="item_id")
           .merge(imdet[["item_id", "realized"]].rename(columns={"realized": "improved_service"}), on="item_id"))
    out.round(3).to_csv(data_dir / "policy_comparison_sample.csv", index=False)
    print("Exported policy_comparison_sample.csv with", len(out), "items")


if __name__ == "__main__":
    main()
