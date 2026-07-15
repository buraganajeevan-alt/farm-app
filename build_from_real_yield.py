"""
build_from_real_yield.py
------------------------
Builds the project dataset from a REAL measured-yield dataset:
  punit_yeild.csv  (241,226 rows)
  Columns present (REAL): Crop, annual_rainfall, yeild (measured),
  Soil Type, Soil pH, State, District, Season, Year, Area, Production.

This is the genuine article: Yield is measured production/area, not derived.

What we have vs. your 10-col schema:
  Crop            <- REAL (Crop)
  Soil_Type       <- REAL (Soil Type)
  Rainfall        <- REAL (annual_rainfall)
  Temperature     <- NOT in source  -> filled from real crop-optima (crop_recommendation.csv)
  Humidity        <- NOT in source  -> filled from real crop-optima
  pH              <- REAL (Soil pH)
  N, P, K        <- NOT in source  -> filled from real crop-optima
  Yield           <- REAL (yeild)

Temperature/Humidity/N/P/K are taken from the separate real crop
recommendation dataset's per-crop means, so they are real agronomic
values (not invented), just not from the same record. Documented in paper.

Output: data/crop_yield.csv  (YOUR 10 columns)
"""
import csv, os, statistics as st

REAL_YIELD = os.path.join("realdata", "real_yield_dataset.csv")
REAL_CROP  = os.path.join("realdata", "crop_recommendation.csv")
OUT = os.path.join("data", "crop_yield.csv")

# --- load real crop-recommendation means (N,P,K,temp,humidity,ph,rain) ---
crop_opt = {}
with open(REAL_CROP) as f:
    for r in csv.DictReader(f):
        c = r["label"].strip().lower()
        d = crop_opt.setdefault(c, {"N":[], "P":[], "K":[], "temp":[],
                                     "hum":[], "ph":[], "rain":[]})
        d["N"].append(float(r["N"])); d["P"].append(float(r["P"]))
        d["K"].append(float(r["K"])); d["temp"].append(float(r["temperature"]))
        d["hum"].append(float(r["humidity"])); d["ph"].append(float(r["ph"]))
        d["rain"].append(float(r["rainfall"]))
for c, d in crop_opt.items():
    for k in d:
        d[k] = st.mean(d[k])

# map dataset crop names -> recommendation crop names where possible
def match_crop(name):
    n = name.strip().lower()
    # direct
    if n in crop_opt: return n
    # fuzzy contain
    for k in crop_opt:
        if k in n or n in k:
            return k
    return None

# Real soil types present in source; keep as-is.
os.makedirs("data", exist_ok=True)
n_written = 0
n_skipped = 0
seen_crops = set()

with open(REAL_YIELD, encoding="utf-8") as fin, \
     open(OUT, "w", newline="") as fout:
    rd = csv.DictReader(fin)
    w = csv.writer(fout)
    w.writerow(["Crop","Soil_Type","Rainfall","Temperature","Humidity",
                "pH","N","P","K","Yield"])
    for row in rd:
        try:
            crop = row["Crop"].strip().capitalize()
            soil = row["Soil Type"].strip()
            rain = float(row["annual_rainfall"])
            ph = float(row["Soil pH"])
            yld = float(row["yeild"])
        except (ValueError, KeyError):
            n_skipped += 1
            continue
        if yld <= 0 or rain <= 0 or ph <= 0:
            n_skipped += 1
            continue
        # optional inputs from real crop-optima if crop matches
        mc = match_crop(row["Crop"])
        if mc:
            o = crop_opt[mc]
            temp = round(o["temp"],1); hum = round(o["hum"],1)
            n_ = round(o["N"],1); p_ = round(o["P"],1); k_ = round(o["K"],1)
        else:
            # generic fallback (real recommendation dataset average)
            temp = round(st.mean([v["temp"] for v in crop_opt.values()]),1)
            hum  = round(st.mean([v["hum"] for v in crop_opt.values()]),1)
            n_   = round(st.mean([v["N"] for v in crop_opt.values()]),1)
            p_   = round(st.mean([v["P"] for v in crop_opt.values()]),1)
            k_   = round(st.mean([v["K"] for v in crop_opt.values()]),1)
        w.writerow([crop, soil, round(rain,1), temp, hum,
                    round(ph,2), n_, p_, k_, round(yld,3)])
        seen_crops.add(crop)
        n_written += 1

print(f"REAL yield dataset built: {OUT}")
print(f"  rows written: {n_written} | skipped: {n_skipped}")
print(f"  distinct crops: {len(seen_crops)}")
print("  crops:", ", ".join(sorted(seen_crops)))
