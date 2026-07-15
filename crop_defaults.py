"""
crop_defaults.py
----------------
Provides REAL, data-derived default environmental values for each crop,
so a farmer who only knows their Crop + Soil_Type still gets a sensible
prediction. Defaults come from the real "Crop Recommendation" dataset's
per-crop means (N, P, K, temperature, humidity, pH, rainfall) — i.e.
regional / typical agronomic values (NOT farm-specific).

Design (per our discussion):
  - Farmer enters only Crop + Soil Type (what they know).
  - App auto-fills Rainfall/pH/Temp/Humidity/NPK from these regional
    defaults (stand-in for government open data: IMD, Soil Health Card,
    NBSS&LUP). Farmer may override with their OWN soil-test values.
  - Yield is the model's output, never an input.
"""
import csv, os, statistics as st

SRC = os.path.join("realdata", "crop_recommendation.csv")


def load_defaults():
    """Return dict: crop_lower -> {N,P,K,temp,hum,ph,rain} means."""
    rows = {}
    with open(SRC, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c = r["label"].strip().lower()
            d = rows.setdefault(c, {"N": [], "P": [], "K": [],
                                     "temp": [], "hum": [], "ph": [], "rain": []})
            for k, col in [("N", "N"), ("P", "P"), ("K", "K"),
                          ("temp", "temperature"), ("hum", "humidity"),
                          ("ph", "ph"), ("rain", "rainfall")]:
                try:
                    d[k].append(float(r[col]))
                except (ValueError, KeyError):
                    pass
    out = {}
    for c, d in rows.items():
        out[c] = {k: round(st.mean(v), 2) if v else 0.0 for k, v in d.items()}
    # generic fallback (overall means)
    if out:
        fallback = {k: round(st.mean([o[k] for o in out.values()]), 2)
                    for k in next(iter(out.values()))}
        out["__fallback__"] = fallback
    return out


DEFAULTS = load_defaults()


def default_inputs(crop_name):
    """
    Given a crop name (any case), return a dict of default inputs a farmer
    does NOT need to measure: Rainfall, Temperature, Humidity, pH, N, P, K.
    These are regional/typical values from real data (proxy for government
    open data). The farmer overrides only if they have their own test report.
    """
    key = str(crop_name).strip().lower()
    d = DEFAULTS.get(key) or DEFAULTS.get("__fallback__", {})
    return {
        "Rainfall": d.get("rain", 200),
        "Temperature": d.get("temp", 25),
        "Humidity": d.get("hum", 65),
        "pH": d.get("ph", 6.5),
        "N": d.get("N", 60),
        "P": d.get("P", 40),
        "K": d.get("K", 40),
    }


if __name__ == "__main__":
    for c in ["rice", "wheat", "maize", "cotton"]:
        print(c, "->", default_inputs(c))
