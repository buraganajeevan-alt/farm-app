"""
shc_helper.py
-------------
Local Soil Health Card (SHC) lookup by card ID.

The Government of India Soil Health Card scheme issues each farmer a
unique SHC ID (e.g. "SHC2024AP001") tied to a soil-test report with
pH, Nitrogen (N), Phosphorus (P) and Potassium (K) values.

There is no free public API that resolves an SHC ID to values, so this
module loads a local registry (shc_data.json). In production you would
swap `load_registry()` for a call to the state SHC portal / soil-test
lab database. The lookup is offline and case-insensitive on the ID.

The returned values auto-fill the app's optional Soil Health Card fields,
giving a plot-specific (not just regional) prediction — exactly what the
farmer already has on their physical card.
"""
import os
import json

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "shc_data.json")


def load_registry():
    """Return {shc_id_upper: record} from the local registry file."""
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return {str(k).strip().upper(): v
                for k, v in data.items() if not str(k).startswith("_")}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def lookup(shc_id):
    """
    Given an SHC ID string, return dict:
      {found: bool, shc_id, farmer, village, state, ph, n, p, k}
    Returns found=False (with None values) when the ID is unknown.
    """
    reg = load_registry()
    key = (shc_id or "").strip().upper()
    rec = reg.get(key)
    if not rec:
        return {"found": False, "shc_id": key,
                "farmer": None, "village": None, "state": None,
                "ph": None, "n": None, "p": None, "k": None}
    return {
        "found": True,
        "shc_id": key,
        "farmer": rec.get("farmer"),
        "village": rec.get("village"),
        "state": rec.get("state"),
        "ph": rec.get("ph"),
        "n": rec.get("n"),
        "p": rec.get("p"),
        "k": rec.get("k"),
    }


if __name__ == "__main__":
    print(lookup("shc2024ap001"))   # sample hit (case-insensitive)
    print(lookup("unknown123"))      # miss
