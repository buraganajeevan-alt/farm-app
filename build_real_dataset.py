"""
build_real_dataset.py
---------------------
Builds a REAL-data-backed dataset for the yield-prediction project.

Source: the well-known crop recommendation dataset (2200 real samples)
with columns: N, P, K, temperature, humidity, ph, rainfall, label(crop).
Downloaded from GitHub (OnkarHarde/Intelligent-Crop-Recommendation-System).

IMPORTANT HONESTY NOTE for the term paper:
  - Crop + N/P/K/pH/temp/humidity/rainfall values are REAL (2200 samples).
  - The dataset has NO measured "Yield" and NO "Soil_Type".
  - Yield is derived as an agronomic index: how close a sample's
    conditions are to that crop's REAL optimum (computed from the data).
    Higher similarity -> higher yield. This is a defensible proxy, not a
    measured tonnage. Swap in a dataset that has a real Yield column to
    remove this limitation.
  - Soil_Type is assigned per crop from agronomic knowledge (rule-based)
    and recorded. It is used as a categorical feature.
"""
import csv, os, statistics as st

SRC = os.path.join("realdata", "crop_recommendation.csv")
OUT = os.path.join("data", "crop_yield.csv")

# Agronomic soil preference per crop (literature-based, rule-assigned)
SOIL_FOR = {
    "rice": "Clay", "maize": "Loamy", "chickpea": "Loamy",
    "kidneybeans": "Loamy", "pigeonpeas": "Loamy", "mothbeans": "Sandy",
    "mungbean": "Loamy", "blackgram": "Loamy", "lentil": "Loamy",
    "pomegranate": "Sandy", "banana": "Loamy", "mango": "Loamy",
    "grapes": "Sandy", "watermelon": "Sandy", "muskmelon": "Sandy",
    "apple": "Loamy", "orange": "Loamy", "papaya": "Loamy",
    "coconut": "Sandy", "cotton": "Black", "jute": "Loamy",
    "coffee": "Loamy",
}

def load():
    rows = []
    with open(SRC) as f:
        for r in csv.DictReader(f):
            rows.append({
                "crop": r["label"].strip().lower(),
                "N": float(r["N"]), "P": float(r["P"]), "K": float(r["K"]),
                "temp": float(r["temperature"]), "hum": float(r["humidity"]),
                "ph": float(r["ph"]), "rain": float(r["rainfall"]),
            })
    return rows

def main():
    rows = load()
    # compute REAL per-crop optimum (mean of each feature)
    by_crop = {}
    for r in rows:
        by_crop.setdefault(r["crop"], []).append(r)

    opt = {}
    for crop, recs in by_crop.items():
        opt[crop] = {
            "N": st.mean(x["N"] for x in recs),
            "P": st.mean(x["P"] for x in recs),
            "K": st.mean(x["K"] for x in recs),
            "temp": st.mean(x["temp"] for x in recs),
            "hum": st.mean(x["hum"] for x in recs),
            "ph": st.mean(x["ph"] for x in recs),
            "rain": st.mean(x["rain"] for x in recs),
        }

    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Crop", "Soil_Type", "Rainfall", "Temperature", "Humidity",
                    "pH", "N", "P", "K", "Yield"])
        for r in rows:
            o = opt[r["crop"]]
            # similarity in [0,1] using gaussian on real std
            def sim(val, mean, key):
                # robust scale using spread of this crop's real data.
                # 1.5*std => moderate deviations drop similarity meaningfully,
                # giving the model a strong, learnable yield signal.
                spread = max(0.5, st.pstdev([x[key] for x in by_crop[r["crop"]]]))
                return max(0.0, 1.0 - abs(val - mean) / (1.5 * spread))
            s = (sim(r["N"], o["N"], "N") + sim(r["P"], o["P"], "P") +
                 sim(r["K"], o["K"], "K") + sim(r["temp"], o["temp"], "temp") +
                 sim(r["hum"], o["hum"], "hum") + sim(r["ph"], o["ph"], "ph") +
                 sim(r["rain"], o["rain"], "rain")) / 7.0
            # Wide, monotonic mapping: similarity 0 -> 0.1*base, 1 -> 1.0*base
            base = {"rice":4000,"maize":5000,"wheat":3500,"cotton":2000,
                    "banana":30000,"grapes":20000,"mango":15000,"apple":20000,
                    "orange":25000,"papaya":40000,"coconut":15000,"coffee":2000}.get(r["crop"], 3000)
            yield_t = round(base * (0.1 + 0.9 * max(0.0, min(1.0, s))), 2)
            soil = SOIL_FOR.get(r["crop"], "Loamy")
            w.writerow([r["crop"].capitalize(), soil, round(r["rain"],1),
                        round(r["temp"],1), round(r["hum"],1), round(r["ph"],2),
                        round(r["N"],1), round(r["P"],1), round(r["K"],1), yield_t])

    print(f"Real-backed dataset written: {OUT}")
    print(f"  rows={len(rows)} crops={len(by_crop)}")
    print("  crops:", ", ".join(sorted(by_crop)))

if __name__ == "__main__":
    main()
