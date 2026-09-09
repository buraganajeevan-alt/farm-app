"""weather_service.py — Live 3-Day Agricultural Weather Forecast Engine.
Uses Open-Meteo Global Weather API (100% Free, 0 API Keys, 0 Cost).
Fetches high-resolution daily weather (Temp, Rain mm, Rain Prob %, Wind) for GPS/State
and generates automated, actionable agricultural advisories for farmers.
"""
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

# WMO Weather Code Mappings -> (Icon, Description)
WMO_CODES = {
    0: ("☀️", "Clear Sky"),
    1: ("🌤️", "Mainly Clear"),
    2: ("⛅", "Partly Cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Foggy"),
    48: ("🌫️", "Depositing Rime Fog"),
    51: ("🌦️", "Light Drizzle"),
    53: ("🌦️", "Moderate Drizzle"),
    55: ("🌦️", "Dense Drizzle"),
    61: ("🌧️", "Slight Rain"),
    63: ("🌧️", "Moderate Rain"),
    65: ("🌧️", "Heavy Rain"),
    80: ("🌧️", "Slight Rain Showers"),
    81: ("🌧️", "Moderate Showers"),
    82: ("🌧️", "Violent Showers"),
    95: ("⛈️", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm with Hail"),
    99: ("⛈️", "Heavy Thunderstorm"),
}

DEFAULT_COORDINATES = {
    "lat": 16.52,
    "lon": 80.63,
    "location_name": "Andhra Pradesh (Central)"
}


def get_coordinates_for_state(state_name: str):
    """Resolves latitude and longitude for an Indian state using geo_state anchors."""
    try:
        from geo_state import ANCHORS
        if state_name in ANCHORS and ANCHORS[state_name]:
            city, lat, lon = ANCHORS[state_name][0]
            return lat, lon, f"{city}, {state_name}"
    except Exception as e:
        logger.warning("Failed resolving state anchor for %s: %s", state_name, e)
    return DEFAULT_COORDINATES["lat"], DEFAULT_COORDINATES["lon"], DEFAULT_COORDINATES["location_name"]


def generate_day_advisory(rain_prob: int, rain_mm: float, temp_max: float, wind_kmh: float) -> str:
    """Generates an agronomic field advisory based on single-day forecast parameters."""
    if rain_prob >= 60 or rain_mm >= 5.0:
        return "🌧️ High Rain Risk: Postpone Urea top-dressing & chemical sprays for 48h to prevent leaching. Ensure drainage channels are open."
    elif rain_prob >= 35 or rain_mm >= 2.0:
        return "🌦️ Moderate Rain Alert: Avoid foliar spray today. Keep harvested crop under tarpaulin cover."
    elif wind_kmh >= 22.0:
        return "💨 High Wind Alert: Avoid pesticide/herbicide spraying today due to spray drift risk."
    elif temp_max >= 38.0:
        return "🔥 Heat Stress Alert: Irrigate in early morning or late evening to prevent evaporation loss."
    else:
        return "☀️ Favorable Conditions: Ideal for land preparation, weeding, and balanced fertilizer application."


def get_3day_weather(lat=None, lon=None, state_name=None):
    """
    Fetches 3-day weather forecast from Open-Meteo and generates agricultural advisories.
    Returns: dict with forecast_days (list of 3 days), location, and summary_advisory.
    """
    location_label = "Local Farm GPS"
    try:
        if lat is not None and lon is not None:
            lat = float(lat)
            lon = float(lon)
            if state_name:
                location_label = f"{state_name} ({lat:.2f}, {lon:.2f})"
            else:
                location_label = f"GPS ({lat:.2f}, {lon:.2f})"
        elif state_name:
            lat, lon, location_label = get_coordinates_for_state(state_name)
        else:
            lat, lon, location_label = DEFAULT_COORDINATES["lat"], DEFAULT_COORDINATES["lon"], DEFAULT_COORDINATES["location_name"]
    except Exception:
        lat, lon, location_label = DEFAULT_COORDINATES["lat"], DEFAULT_COORDINATES["lon"], DEFAULT_COORDINATES["location_name"]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "weathercode",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "windspeed_10m_max"
        ],
        "timezone": "auto",
        "forecast_days": 3
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json().get("daily", {})
            times = data.get("time", [])
            wcodes = data.get("weathercode", [])
            t_max = data.get("temperature_2m_max", [])
            t_min = data.get("temperature_2m_min", [])
            precip = data.get("precipitation_sum", [])
            precip_prob = data.get("precipitation_probability_max", [])
            wind = data.get("windspeed_10m_max", [])

            forecast_days = []
            max_rain_seen = 0.0
            max_prob_seen = 0

            for i in range(min(3, len(times))):
                date_str = times[i]
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    day_name = "Today" if i == 0 else ("Tomorrow" if i == 1 else dt.strftime("%A"))
                    display_date = dt.strftime("%b %d")
                except Exception:
                    day_name = f"Day {i+1}"
                    display_date = date_str

                code = wcodes[i] if i < len(wcodes) else 0
                icon, desc = WMO_CODES.get(code, ("⛅", "Partly Cloudy"))
                t_hi = round(t_max[i], 1) if i < len(t_max) else 30.0
                t_lo = round(t_min[i], 1) if i < len(t_min) else 22.0
                r_mm = round(precip[i], 1) if i < len(precip) else 0.0
                r_pct = int(precip_prob[i]) if i < len(precip_prob) and precip_prob[i] is not None else 0
                w_speed = round(wind[i], 1) if i < len(wind) else 10.0

                if r_mm > max_rain_seen: max_rain_seen = r_mm
                if r_pct > max_prob_seen: max_prob_seen = r_pct

                day_advisory = generate_day_advisory(r_pct, r_mm, t_hi, w_speed)

                forecast_days.append({
                    "day_label": day_name,
                    "date": display_date,
                    "icon": icon,
                    "condition": desc,
                    "temp_max": t_hi,
                    "temp_min": t_lo,
                    "rain_prob": r_pct,
                    "rain_mm": r_mm,
                    "wind_kmh": w_speed,
                    "advisory": day_advisory
                })

            # Overall 3-Day Agricultural Synthesis
            if max_prob_seen >= 55 or max_rain_seen >= 4.0:
                summary_advisory = f"⚠️ 3-Day Weather Advisory: Rain expected ({max_rain_seen} mm, {max_prob_seen}% probability). Hold chemical spraying and Urea top-dressing. Inspect field drainage."
            else:
                summary_advisory = "✅ 3-Day Weather Advisory: Weather is mostly favorable for farming operations and irrigation management."

            return {
                "status": "ok",
                "location": location_label,
                "forecast_days": forecast_days,
                "summary_advisory": summary_advisory
            }
    except Exception as e:
        logger.error("Open-Meteo forecast error: %s", e)

    # Graceful Fallback if offline or network unavailable
    return {
        "status": "fallback",
        "location": location_label,
        "forecast_days": [
            {"day_label": "Today", "date": "Day 1", "icon": "☀️", "condition": "Sunny", "temp_max": 32, "temp_min": 24, "rain_prob": 10, "rain_mm": 0, "wind_kmh": 12, "advisory": "☀️ Favorable conditions for field work."},
            {"day_label": "Tomorrow", "date": "Day 2", "icon": "⛅", "condition": "Partly Cloudy", "temp_max": 31, "temp_min": 23, "rain_prob": 20, "rain_mm": 0.5, "wind_kmh": 11, "advisory": "⛅ Good weather for crop inspection."},
            {"day_label": "Day 3", "date": "Day 3", "icon": "🌤️", "condition": "Mostly Clear", "temp_max": 33, "temp_min": 24, "rain_prob": 15, "rain_mm": 0, "wind_kmh": 10, "advisory": "☀️ Normal farming conditions."}
        ],
        "summary_advisory": "ℹ️ 3-Day Weather: Clear to partly cloudy. Suitable for routine agricultural operations."
    }
