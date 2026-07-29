"""crop_defaults.py
Per-crop TYPICAL agronomic defaults derived from the REAL crop_recommendation.csv.
These are the auto-fill values a farmer sees; overridable with Soil Health Card / IMD.
"""
import csv
from collections import defaultdict

def load_crop_defaults():
    d = defaultdict(lambda: defaultdict(list))
    with open("realdata/crop_recommendation.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c = r["label"].strip().lower()
            for k in ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]:
                try:
                    d[c][k].append(float(r[k]))
                except: pass
    out = {}
    for c, vals in d.items():
        out[c] = {k: round(sum(v) / len(v), 2) for k, v in vals.items()}
    return out

CROP_DEFAULTS = load_crop_defaults()

def default_for(crop):
    crop = (crop or "").strip().lower()
    return CROP_DEFAULTS.get(crop, {})
