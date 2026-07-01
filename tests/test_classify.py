import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from inventory_policy import generate

def test_abc_and_service_attached():
    items = generate()["items"]
    assert set(items["abc"]) <= {"A", "B", "C"}
    for cls, sl in {"A": 0.98, "B": 0.95, "C": 0.90}.items():
        sub = items[items["abc"] == cls]
        if len(sub):
            assert (sub["service_level"] == sl).all()
