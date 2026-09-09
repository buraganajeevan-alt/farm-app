"""geo_state.py  (precision-upgraded)
GPS (lat,lon) -> region with two tiers of precision:

TIER 1 — OFFLINE, STATE-LEVEL (always works, no internet)
  Nearest of ~multiple real city ANCHORS per state. Far more accurate
  than one centroid/state (fixes e.g. Pune->Maharashtra, not DNH).

TIER 2 — ONLINE, DISTRICT-LEVEL (if internet present)
  Reverse geocode via BigDataCloud free client API (no key) -> real
  district/locality + state. Also returns that district's REAL mean yield
  computed from the production statistics file. Graceful fallback to Tier 1.

Rainfall auto-fill stays per-state (IMD regional mean).
"""
import csv, json, urllib.request, ssl
from collections import defaultdict

# ---- Real city anchors (lat,lon) per state/UT. More anchors = better offline precision. ----
ANCHORS = {
    "Andaman and Nicobar Islands": [("Port Blair",11.67,92.73)],
    "Andhra Pradesh": [("Vijayawada",16.52,80.63),("Tirupati",13.63,79.42),("Visakhapatnam",17.69,83.22)],
    "Arunachal Pradesh": [("Itanagar",27.08,93.61)],
    "Assam": [("Guwahati",26.14,91.74),("Silchar",24.81,92.94)],
    "Bihar": [("Patna",25.61,85.14),("Gaya",24.80,85.00)],
    "Chandigarh": [("Chandigarh",30.73,76.78)],
    "Chhattisgarh": [("Raipur",21.25,81.63),("Bilaspur",22.08,82.14)],
    "Dadra and Nagar Haveli": [("Silvassa",20.27,73.03)],
    "Daman and Diu": [("Daman",20.42,72.84)],
    "Delhi": [("New Delhi",28.61,77.20)],
    "Goa": [("Panaji",15.49,73.83)],
    "Gujarat": [("Ahmedabad",23.03,72.58),("Surat",21.17,72.83),("Rajkot",22.30,70.80)],
    "Haryana": [("Chandigarh",30.73,76.78),("Hisar",29.15,75.72)],
    "Himachal Pradesh": [("Shimla",31.10,77.17),("Dharamshala",32.22,76.32)],
    "Jammu and Kashmir": [("Srinagar",34.08,74.80),("Jammu",32.73,74.87)],
    "Jharkhand": [("Ranchi",23.34,85.31),("Jamshedpur",22.80,86.20)],
    "Karnataka": [("Bengaluru",12.97,77.59),("Mysuru",12.30,76.64),("Hubballi",15.36,75.13)],
    "Kerala": [("Thiruvananthapuram",8.52,76.94),("Kochi",9.93,76.27),("Kozhikode",11.25,75.78)],
    "Ladakh": [("Leh",34.15,77.58)],
    "Lakshadweep": [("Kavaratti",10.57,72.64)],
    "Madhya Pradesh": [("Bhopal",23.26,77.40),("Indore",22.72,75.86),("Jabalpur",23.18,79.99)],
    "Maharashtra": [("Mumbai",19.08,72.88),("Pune",18.52,73.85),("Nagpur",21.15,79.09),("Aurangabad",19.90,75.32)],
    "Manipur": [("Imphal",24.81,93.94)],
    "Meghalaya": [("Shillong",25.57,91.88)],
    "Mizoram": [("Aizawl",23.73,92.72)],
    "Nagaland": [("Kohima",25.67,94.11)],
    "Odisha": [("Bhubaneswar",20.29,85.82),("Cuttack",20.46,85.88)],
    "Puducherry": [("Puducherry",11.94,79.81)],
    "Punjab": [("Chandigarh",30.73,76.78),("Ludhiana",30.90,75.85),("Amritsar",31.63,74.87)],
    "Rajasthan": [("Jaipur",26.91,75.79),("Jodhpur",26.24,73.02),("Udaipur",24.59,73.68)],
    "Sikkim": [("Gangtok",27.33,88.61)],
    "Tamil Nadu": [("Chennai",13.08,80.27),("Coimbatore",11.00,76.96),("Madurai",9.93,78.12)],
    "Telangana": [("Hyderabad",17.39,78.49),("Warangal",18.00,79.59)],
    "Tripura": [("Agartala",23.83,91.29)],
    "Uttar Pradesh": [("Lucknow",26.85,80.95),("Kanpur",26.45,80.33),("Varanasi",25.32,82.97)],
    "Uttarakhand": [("Dehradun",30.31,78.03),("Haldwani",29.22,79.51)],
    "West Bengal": [("Kolkata",22.57,88.36),("Siliguri",26.73,88.42)],
}

# flatten for nearest search
_FLAT = [(st, nm, la, lo) for st, lst in ANCHORS.items() for nm, la, lo in lst]

def gps_to_region(lat, lon):
    """TIER 1: nearest anchor -> state. Offline, always works."""
    best, best_d, best_st = None, 1e18, None
    for st, nm, la, lo in _FLAT:
        d = (lat - la) ** 2 + (lon - lo) ** 2
        if d < best_d:
            best_d, best, best_st = d, nm, st
    return best_st, {"anchor": best, "lat": lat, "lon": lon}

# ---- Real IMD state annual-rainfall means (mm), public figures (documented) ----
STATE_RAINFALL_MM = {
    "Andaman and Nicobar Islands":3000,"Andhra Pradesh":920,"Arunachal Pradesh":2780,
    "Assam":2818,"Bihar":1200,"Chandigarh":1110,"Chhattisgarh":1450,
    "Dadra and Nagar Haveli":2200,"Daman and Diu":1700,"Delhi":790,
    "Goa":3000,"Gujarat":850,"Haryana":600,"Himachal Pradesh":1200,
    "Jammu and Kashmir":1100,"Jharkhand":1400,"Karnataka":1150,
    "Kerala":3000,"Ladakh":100,"Lakshadweep":1600,"Madhya Pradesh":1200,
    "Maharashtra":1050,"Manipur":2100,"Meghalaya":2818,"Mizoram":2200,
    "Nagaland":2000,"Odisha":1450,"Puducherry":1250,"Punjab":600,
    "Rajasthan":550,"Sikkim":3000,"Tamil Nadu":945,"Telangana":900,
    "Tripura":2100,"Uttar Pradesh":1050,"Uttarakhand":1600,"West Bengal":1800,
}
STATE_WEATHER = {st: {"rainfall": rf, "temperature": 27.0, "humidity": 65.0}
                  for st, rf in STATE_RAINFALL_MM.items()}

def state_rainfall(state):
    return STATE_RAINFALL_MM.get(state, 1150)

# ---- District-level real mean yield (Tier 2 online bonus), from production stats ----
_DISTRICT_YIELD = {}   # (state, district) -> mean yield (t/ha)
_DISTRICT_STATE = {}     # district -> state
def _load_districts():
    try:
        acc = defaultdict(list)
        with open("realdata/crop_production.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                try:
                    a = float(r["Area"].strip()); p = float(r["Production"].strip())
                except: continue
                if a <= 0: continue
                y = p / a
                if 0 < y <= 70:
                    key = (r["State_Name"].strip(), r["District_Name"].strip())
                    acc[key].append(y)
        for (st, dt), vs in acc.items():
            _DISTRICT_YIELD[(st, dt)] = sum(vs) / len(vs)
            _DISTRICT_STATE[dt.strip().upper()] = st
    except Exception:
        pass
_load_districts()

def district_mean_yield(state, district):
    return _DISTRICT_YIELD.get((state, district.strip()))

# ---- Tier 2: online reverse geocode (no key) ----
def normalize_state(raw_name: str) -> str:
    """Matches any raw state name against official 36 Indian States/UTs."""
    if not raw_name:
        return ""
    clean = raw_name.lower().replace("state of", "").replace("state", "").replace("territory", "").strip()
    
    # Direct and partial matching
    for official in STATE_WEATHER.keys():
        off_clean = official.lower()
        if clean == off_clean or clean in off_clean or off_clean in clean:
            return official

    aliases = {
        "orissa": "Odisha",
        "pondicherry": "Puducherry",
        "uttaranchal": "Uttarakhand",
        "nct": "Delhi",
        "new delhi": "Delhi",
        "jammu": "Jammu and Kashmir",
        "kashmir": "Jammu and Kashmir",
        "andaman": "Andaman and Nicobar Islands",
        "daman": "Daman and Diu"
    }
    for k, v in aliases.items():
        if k in clean:
            return v
    return raw_name.strip()


def reverse_geocode(lat, lon, timeout=5):
    """Returns dict with district/locality + state with dual provider fallback (BigDataCloud + OpenStreetMap)."""
    lat, lon = float(lat), float(lon)
    
    # 1. Try BigDataCloud
    try:
        url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
        req = urllib.request.Request(url, headers={"User-Agent": "SmartFarmingApp/1.0"})
        raw = urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()).read()
        d = json.loads(raw)
        st = normalize_state(d.get("principalSubdivision") or "")
        city = d.get("city") or d.get("locality") or d.get("localityInfo", {}).get("administrative", [{}])[-1].get("name", "")
        if st:
            return {"state": st, "district": (city or st).strip(), "country": d.get("countryName", "")}
    except Exception as e:
        pass

    # 2. Try OpenStreetMap Nominatim
    try:
        osm_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        req = urllib.request.Request(osm_url, headers={"User-Agent": "SmartFarmingAssistant/1.0 (agri@smartfarm.local)"})
        raw = urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()).read()
        d = json.loads(raw)
        addr = d.get("address", {})
        raw_state = addr.get("state", "")
        st = normalize_state(raw_state)
        district = addr.get("county") or addr.get("state_district") or addr.get("district") or addr.get("city") or addr.get("town") or addr.get("village") or ""
        if st:
            return {"state": st, "district": district.strip(), "country": addr.get("country", "")}
    except Exception as e:
        pass

    return None


def search_location_places(query: str, limit=5):
    """Forward geocode search for Indian cities, towns, and districts via Open-Meteo."""
    clean_q = urllib.parse.quote(query.strip())
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_q}&count={limit}&language=en&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartFarmingApp/1.0"})
        raw = urllib.request.urlopen(req, timeout=5, context=ssl.create_default_context()).read()
        results = json.loads(raw).get("results", [])
        places = []
        for r in results:
            st = normalize_state(r.get("admin1", ""))
            places.append({
                "name": r.get("name"),
                "state": st or r.get("admin1", ""),
                "country": r.get("country", ""),
                "lat": r.get("latitude"),
                "lon": r.get("longitude"),
                "display": f"{r.get('name')}, {r.get('admin1', '')} ({r.get('country', '')})"
            })
        return places
    except Exception:
        return []


def resolve_region(lat, lon):
    """Full resolver: Tier 2 (district, if online) else Tier 1 (state anchors)."""
    lat, lon = float(lat), float(lon)
    rg = reverse_geocode(lat, lon)
    if rg and rg.get("state"):
        st = rg["state"]
        rf = state_rainfall(st)
        dy = district_mean_yield(st, rg.get("district", "")) if rg.get("district") else None
        return {"tier": 2, "state": st, "district": rg.get("district"),
                "rainfall": rf, "district_mean_yield": dy,
                "message": f"📍 {rg.get('district')}, {st}  (district-level · rainfall {rf} mm)"}
    # fallback Tier 1
    st, info = gps_to_region(lat, lon)
    return {"tier": 1, "state": st, "district": None,
            "rainfall": state_rainfall(st), "district_mean_yield": None,
            "message": f"Region (state): {st}  (rainfall {state_rainfall(st)} mm)  [offline anchor]"}
