"""
generate_dataset.py
-------------------
Creates a realistic synthetic agricultural dataset for the
"Smart Farming - AI Based Crop Yield Prediction" project.

Why synthetic?  So the project runs end-to-end out of the box.
Each crop has biologically-plausible preferences (ideal soil types,
pH range, NPK balance, rainfall, temperature, humidity). Yield is
modelled as highest when conditions match the crop's optimum and
degrades (with noise) as they diverge.

HOW TO USE REAL DATA:
Replace data/crop_yield.csv with your own dataset that has the same
columns (Crop, Soil_Type, Rainfall, Temperature, Humidity, pH,
N, P, K, Yield). No code changes needed.
"""
import csv
import os
import random

random.seed(42)

# Crop -> its agronomic optimum / tolerances
# ideal_soil: list of preferred soil types (others get a penalty)
# pH_range: (min, max) ideal
# npk: ideal (N, P, K)
# rain: ideal (mm) ; temp: ideal (C) ; hum: ideal (%)
CROPS = {
    "Rice":      dict(soil=["Clay", "Alluvial", "Loamy"], ph=(5.5, 6.5), npk=(100, 50, 40), rain=200, temp=27, hum=80, base=4.5),
    "Wheat":     dict(soil=["Loamy", "Clay", "Alluvial"], ph=(6.0, 7.5), npk=(80, 40, 30),  rain=100, temp=20, hum=55, base=3.5),
    "Maize":     dict(soil=["Loamy", "Silt", "Alluvial"], ph=(5.8, 7.0), npk=(90, 45, 35),  rain=90,  temp=25, hum=60, base=5.0),
    "Cotton":    dict(soil=["Black", "Loamy", "Red"],     ph=(6.0, 8.0), npk=(70, 35, 35),  rain=70,  temp=28, hum=50, base=2.0),
    "Sugarcane": dict(soil=["Loamy", "Alluvial", "Black"],ph=(6.0, 7.5), npk=(120,60, 60),  rain=150, temp=27, hum=75, base=70.0),
    "Soybean":   dict(soil=["Loamy", "Silt", "Black"],    ph=(6.0, 7.0), npk=(40, 60, 40),  rain=100, temp=25, hum=65, base=2.5),
    "Groundnut": dict(soil=["Sandy", "Loamy", "Red"],     ph=(6.0, 7.0), npk=(30, 50, 30),  rain=80,  temp=28, hum=55, base=1.8),
    "Millet":    dict(soil=["Sandy", "Red", "Loamy"],     ph=(5.5, 7.5), npk=(40, 20, 20),  rain=50,  temp=29, hum=45, base=1.5),
    "Banana":    dict(soil=["Loamy", "Alluvial", "Silt"], ph=(5.5, 7.0), npk=(100,40, 100), rain=120, temp=28, hum=80, base=30.0),
    "Tomato":    dict(soil=["Loamy", "Silt", "Alluvial"], ph=(6.0, 6.8), npk=(100,50, 50),  rain=60,  temp=24, hum=70, base=40.0),
}

SOILS = ["Loamy", "Clay", "Sandy", "Silt", "Black", "Red", "Alluvial", "Laterite"]

N_RECORDS = 6000

os.makedirs("data", exist_ok=True)
out_path = os.path.join("data", "crop_yield.csv")

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

with open(out_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Crop", "Soil_Type", "Rainfall", "Temperature", "Humidity",
                "pH", "N", "P", "K", "Yield"])
    for _ in range(N_RECORDS):
        crop = random.choice(list(CROPS))
        cfg = CROPS[crop]
        soil = random.choice(SOILS)

        # Sample conditions around this crop's optimum
        rain = clamp(random.gauss(cfg["rain"], 40), 20, 400)
        temp = clamp(random.gauss(cfg["temp"], 5), 10, 40)
        hum  = clamp(random.gauss(cfg["hum"], 12), 20, 100)
        ph   = round(clamp(random.gauss(sum(cfg["ph"]) / 2, 1.0), 4.0, 9.0), 1)
        n = clamp(random.gauss(cfg["npk"][0], 30), 0, 250)
        p = clamp(random.gauss(cfg["npk"][1], 20), 0, 150)
        k = clamp(random.gauss(cfg["npk"][2], 25), 0, 250)

        # ---- yield model ----
        # soil penalty: 0 if preferred, ~25% loss otherwise
        soil_pen = 0.0 if soil in cfg["soil"] else 0.25

        # gaussian penalties for being off-optimum
        def pen(val, opt, scale):
            return abs(val - opt) / scale
        pr = pen(rain, cfg["rain"], 120)
        pt = pen(temp, cfg["temp"], 10)
        ph_pen = 0.0 if cfg["ph"][0] <= ph <= cfg["ph"][1] else pen(ph, sum(cfg["ph"]) / 2, 1.5)
        pn = pen(n, cfg["npk"][0], 60)
        pp = pen(p, cfg["npk"][1], 40)
        pk = pen(k, cfg["npk"][2], 60)
        phum = pen(hum, cfg["hum"], 30)

        # combined stress factor (0 = perfect, larger = worse)
        stress = soil_pen + 0.20 * pr + 0.20 * pt + 0.25 * ph_pen + \
                 0.12 * pn + 0.10 * pp + 0.10 * pk + 0.10 * phum
        stress = clamp(stress, 0, 2.5)

        yield_t = cfg["base"] * max(0.15, (1.0 - 0.45 * stress))
        yield_t = round(max(0.1, yield_t + random.gauss(0, 0.05 * cfg["base"])), 3)

        w.writerow([crop, soil, round(rain, 1), round(temp, 1), round(hum, 1),
                    ph, round(n, 1), round(p, 1), round(k, 1), yield_t])

print(f"Dataset written: {out_path}  ({N_RECORDS} rows)")
