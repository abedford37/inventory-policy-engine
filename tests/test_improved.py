import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from inventory_policy import generate, faithful_policy, improved_policy
from inventory_policy.evaluate import realized_service

def test_min_ophq_max_ordering():
    im = improved_policy(generate()["items"])
    assert (im["min_qty"] <= im["ophq_qty"]).all()
    assert (im["ophq_qty"] <= im["max_qty"]).all()

def test_safety_stock_nonnegative():
    im = improved_policy(generate()["items"])
    assert (im["safety_stock"] >= 0).all()

def test_improved_hits_targets_by_abc():
    items = generate()["items"]
    det = realized_service(items, improved_policy(items))
    for cls in ("A", "B", "C"):
        sub = det[det["abc"] == cls]
        assert abs(sub["realized"].mean() - sub["target"].mean()) < 0.03

def test_faithful_underdelivers_vs_improved():
    items = generate()["items"]
    f = realized_service(items, faithful_policy(items))["realized"].mean()
    im = realized_service(items, improved_policy(items))["realized"].mean()
    assert f < im and f < 0.75

def test_import_carries_more_safety_stock():
    items = generate()["items"]
    det = realized_service(items, improved_policy(items))
    by = det.groupby("origin")["safety_stock"].sum()
    assert by["import"] > by["domestic"]
