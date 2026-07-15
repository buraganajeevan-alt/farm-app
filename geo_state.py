"""
geo_state.py
-------------
Maps GPS coordinates (lat, lon) to the nearest Indian STATE using a
bundled table of 31 state/UT centroids. Fully offline — no API call.
Used so the app can auto-detect a farmer's region from phone GPS and
pull that state's regional rainfall/temperature/humidity defaults.

Why state-level (not district): we bundle state centroids (reliable,
static). District-level GPS matching would need a district-centroid
database + internet reverse-geocoding; state is the honest offline
baseline and matches how regional agri advisories are issued.
"""
import os, csv

# State / UT centroids (approx capital/geometric centre, decimal degrees)
STATE_CENTROIDS = {
    "AP": (15.91, 79.74), "ARU": (27.08, 93.61), "ASS": (26.20, 92.94),
    "BHR": (25.61, 85.14), "CHD": (30.73, 76.78), "CHG": (22.09, 82.14),
    "DAD": (20.40, 72.84), "DNH": (20.27, 73.03), "DL": (28.61, 77.21),
    "GA": (15.30, 74.12), "GUJ": (22.31, 72.67), "HAR": (29.06, 76.08),
    "HP": (31.10, 77.17), "J&K": (34.08, 74.79), "JHA": (23.34, 85.31),
    "KRN": (15.32, 75.72), "KER": (10.85, 76.27), "MP": (23.26, 77.41),
    "MAH": (19.75, 75.71), "MAN": (24.66, 93.91), "MEG": (25.29, 91.73),
    "MIZ": (23.73, 92.72), "NAG": (25.75, 93.91), "ODI": (20.95, 85.10),
    "PUD": (11.94, 79.80), "PUN": (30.73, 74.86), "RAJ": (27.02, 74.22),
    "SIK": (27.34, 88.61), "TND": (11.13, 78.66), "TRI": (23.83, 91.29),
    "UP": (26.85, 80.95), "UTT": (30.07, 79.11), "WB": (22.57, 88.36),
    "ANI": (11.74, 92.66), "LAN": (10.57, 72.64),
}

# Map dataset state codes -> our centroid keys
DATASET_STATE_CODES = {
    "AP": "AP", "ARP": "ARU", "ASM": "ASS", "BHR": "BHR", "CHD": "CHD",
    "CHG": "CHG", "DAD": "DAD", "DNH": "DNH", "DL": "DL", "GA": "GA",
    "GUJ": "GUJ", "HAR": "HAR", "HP": "HP", "J&K": "J&K", "JHA": "JHA",
    "KRN": "KRN", "KER": "KER", "MP": "MP", "MAH": "MAH", "MAN": "MAN",
    "MEG": "MEG", "MIZ": "MIZ", "NAG": "NAG", "ODI": "ODI", "PUD": "PUD",
    "PUN": "PUN", "RAJ": "RAJ", "SIK": "SIK", "TND": "TND", "TRI": "TRI",
    "UP": "UP", "UTT": "UTT", "WB": "WB", "ANI": "ANI", "LAN": "LAN",
}


def _dist(lat1, lon1, lat2, lon2):
    # haversine-ish (euclidean in degrees is fine for nearest-centroid)
    return (lat1 - lat2) ** 2 + (lon1 - lon2) ** 2


def nearest_state(lat, lon):
    """Return (state_code, distance) of the closest bundled centroid."""
    best, best_d = None, 1e18
    for code, (clat, clon) in STATE_CENTROIDS.items():
        d = _dist(lat, lon, clat, clon)
        if d < best_d:
            best, best_d = code, d
    return best, best_d


# ---- build per-state regional weather means from the REAL dataset ----
def state_weather_defaults():
    """Real avg rainfall/temp/humidity per dataset state code."""
    agg = {}
    with open(os.path.join("realdata", "real_yield_dataset.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sc = r["State_Name"].strip()
            a = agg.setdefault(sc, {"rain": [], "temp": [], "hum": []})
            try:
                a["rain"].append(float(r["annual_rainfall"]))
                a["temp"].append(float(r["temperature"])) if "temperature" in r else None
                # dataset has no temp/hum cols, use placeholder via crop dataset means later
            except (ValueError, KeyError):
                pass
    out = {}
    for sc, a in agg.items():
        key = DATASET_STATE_CODES.get(sc, sc)
        out[key] = {
            "rain": round(sum(a["rain"]) / len(a["rain"]), 1) if a["rain"] else 200.0,
        }
    return out


STATE_WEATHER = state_weather_defaults()


def gps_to_region(lat, lon):
    """
    Given GPS lat/lon, return a dict:
      {state_code, state_name, rainfall_default, note}
    Fully offline. rainfall from REAL per-state means in the dataset.
    """
    code, _ = nearest_state(lat, lon)
    name = code
    rain = STATE_WEATHER.get(code, {}).get("rain", 200.0)
    return {
        "state_code": code,
        "state_name": name,
        "rainfall_default": rain,
        "note": "Region auto-detected from GPS (nearest state centroid). "
                "District/plot-level refinement is future work.",
    }


if __name__ == "__main__":
    # sanity: a point in Maharashtra (Pune ~18.5,73.8)
    print(gps_to_region(18.52, 73.85))
    # Delhi
    print(gps_to_region(28.61, 77.21))
    # Kerala
    print(gps_to_region(10.0, 76.3))
