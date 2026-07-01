import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from inventory_policy import generate, faithful_policy

def test_reproduces_formula():
    items = generate()["items"]
    f = faithful_policy(items).set_index("item_id")
    base = (items.set_index("item_id")["lead_time_days"] * items.set_index("item_id")["daily_mean"])
    assert np.allclose(f["min_qty"], (base * 1.04).round(1))
    assert np.allclose(f["max_qty"], (base * 1.28).round(1))
    assert np.allclose(f["qty_multiple"], (base * 0.84).round(1))

def test_min_below_max():
    f = faithful_policy(generate()["items"])
    assert (f["min_qty"] < f["max_qty"]).all()
