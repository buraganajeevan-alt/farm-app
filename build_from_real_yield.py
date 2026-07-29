"""build_from_real_yield.py  (REVISED — Option A: real district-level weather)
Builds a clean 10-column modelling CSV from THREE real, public sources:
  1) realdata/crop_production.csv     -> State/District/Crop/Area/Production (Indian agri stats)
  2) realdata/crop_recommendation.csv -> per-crop agronomic means (N,P,K,temp,humidity,ph)
  3) realdata/district_rainfall.csv    -> REAL district-level ANNUAL rainfall (IMD, public)

KEY FIX: rainfall is now the REAL per-district value (varies record-to-record),
NOT a constant per-crop mean. This gives the model real weather signal so it
can learn weather->yield (previously rainfall/temp/humidity had ~0 importance).
Soil_Type: coarse dominant-order proxy by state (NBSS&LUP, documented).
"""
import csv, json
from collections import defaultdict

PROD = "realdata/crop_production.csv"
RECO = "realdata/crop_recommendation.csv"
RAIN = "realdata/district_rainfall.csv"
OUT  = "data/crop_yield.csv"

STATE_SOIL = {
    "Andaman and Nicobar Islands":"Loamy","Andhra Pradesh":"Red","Arunachal Pradesh":"Loamy",
    "Assam":"Alluvial","Bihar":"Alluvial","Chandigarh":"Loamy","Chhattisgarh":"Red",
    "Dadra and Nagar Haveli":"Loamy","Daman and Diu":"Loamy","Delhi":"Loamy",
    "Goa":"Laterite","Gujarat":"Black","Haryana":"Loamy","Himachal Pradesh":"Brown",
    "Jammu and Kashmir":"Brown","Jharkhand":"Red","Karnataka":"Red","Kerala":"Laterite",
    "Ladakh":"Brown","Lakshadweep":"Loamy","Madhya Pradesh":"Black","Maharashtra":"Black",
    "Manipur":"Loamy","Meghalaya":"Laterite","Mizoram":"Loamy","Nagaland":"Loamy",
    "Odisha":"Red","Puducherry":"Loamy","Punjab":"Loamy","Rajasthan":"Desert",
    "Sikkim":"Loamy","Tamil Nadu":"Red","Telangana":"Red","Tripura":"Loamy",
    "Uttar Pradesh":"Alluvial","Uttarakhand":"Brown","West Bengal":"Alluvial",
}

# ---- 1. REAL district rainfall (annual, mm) ----
district_rain = {}
with open(RAIN, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        st = r["STATE_UT_NAME"].strip().upper()
        dt = r["DISTRICT"].strip().upper()
        try:
            ann = float(r["ANNUAL"])
        except:
            continue
        if ann <= 0:
            continue
        district_rain[(st, dt)] = ann
        # also keep a state average fallback
        district_rain.setdefault(("__STATE__", st), []).append(ann)

# state-average rainfall (for records whose exact district isn't in the rainfall file)
state_avg_rain = {}
for (k, st), v in list(district_rain.items()):
    if k == "__STATE__":
        state_avg_rain[st] = sum(v) / len(v)

def rainfall_for(state, district):
    st = state.strip().upper(); dt = district.strip().upper()
    if (st, dt) in district_rain:
        return district_rain[(st, dt)]
    if st in state_avg_rain:
        return state_avg_rain[st]
    return 1150.0  # national mean fallback

# ---- 2. per-crop means (N,P,K,temp,humidity,ph) ----
crop_mean = defaultdict(lambda: defaultdict(list))
with open(RECO, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        c = row["label"].strip().lower()
        for k in ["N","P","K","temperature","humidity","ph"]:
            try: crop_mean[c][k].append(float(row[k]))
            except: pass
def mean(lst): return sum(lst)/len(lst) if lst else None
crop_stats = {c: {k: mean(v) for k, v in d.items()} for c, d in crop_mean.items()}

# ---- 3. production -> yield, join REAL district rainfall ----
rows_out = []
with open(PROD, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        try:
            area = float(row["Area"].strip()); prod = float(row["Production"].strip())
        except:
            continue
        if area <= 0: continue
        yield_t = prod / area
        if yield_t <= 0 or yield_t > 70: continue
        crop = row["Crop"].strip().lower()
        state = row["State_Name"].strip()
        district = row["District_Name"].strip()
        soil = STATE_SOIL.get(state, "Loamy")
        cs = crop_stats.get(crop)
        if not cs: continue
        rf = rainfall_for(state, district)
        rows_out.append({
            "Crop": crop, "Soil_Type": soil,
            "Rainfall": round(rf, 1),
            "Temperature": round(cs["temperature"], 2),
            "Humidity": round(cs["humidity"], 2),
            "Soil_pH": round(cs["ph"], 2),
            "N": round(cs["N"], 1), "P": round(cs["P"], 1), "K": round(cs["K"], 1),
            "Yield_tons_per_ha": round(yield_t, 3),
        })

cols = ["Crop","Soil_Type","Rainfall","Temperature","Humidity","Soil_pH","N","P","K","Yield_tons_per_ha"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows_out)

# report
import statistics
crops = sorted(set(r["Crop"] for r in rows_out))
rains = [r["Rainfall"] for r in rows_out]
ys = [r["Yield_tons_per_ha"] for r in rows_out]
print(f"WROTE {OUT}: {len(rows_out)} rows, {len(crops)} crops")
print(f"Rainfall now VARIES: min={min(rains)} max={max(rains)} mean={statistics.mean(rains):.0f} (was constant per crop before)")
print(f"Yield mean={statistics.mean(ys):.2f} median={statistics.median(ys):.2f}")
print("Crops:", crops)
