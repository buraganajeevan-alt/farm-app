"""predict_helper.py
Loads trained model + meta, exposes:
  - predict(crop, soil, **overrides) -> yield + per-feature contribution
  - recommend_crops(soil) -> top-3 crops by mean yield for that soil
  - default_inputs(crop, state) -> auto-fill dict (real per-crop / per-state means)
All inputs default from REAL data; farmer overrides only what they know.
"""
import joblib, numpy as np
from collections import defaultdict
from crop_defaults import CROP_DEFAULTS, default_for
from geo_state import STATE_WEATHER, state_rainfall, gps_to_region

class Predictor:
    def __init__(self):
        self.model = joblib.load("model/yield_model.pkl")
        self.meta = joblib.load("model/meta.pkl")
        self.crops = self.meta["crops"]
        self.soils = self.meta["soils"]
        self.feature_importance = self.meta.get("feature_importance", {})

    def _row(self, crop, soil, rainfall, temp, hum, ph, n, p, k):
        return {
            "Crop": str(crop).strip().lower(),
            "Soil_Type": str(soil).strip(),
            "Rainfall": float(rainfall),
            "Temperature": float(temp),
            "Humidity": float(hum),
            "Soil_pH": float(ph),
            "N": float(n), "P": float(p), "K": float(k),
        }

    def predict(self, crop, soil, rainfall=None, temperature=None, humidity=None,
                soil_ph=None, n=None, p=None, k=None):
        # auto-fill from real defaults if not provided
        cd = default_for(crop)
        rainfall = rainfall if rainfall not in (None, "") else cd.get("rainfall", 1150)
        temperature = temperature if temperature not in (None, "") else cd.get("temperature", 27.0)
        humidity = humidity if humidity not in (None, "") else cd.get("humidity", 65.0)
        soil_ph = soil_ph if soil_ph not in (None, "") else cd.get("ph", 6.5)
        n = n if n not in (None, "") else cd.get("N", 40.0)
        p = p if p not in (None, "") else cd.get("P", 30.0)
        k = k if k not in (None, "") else cd.get("K", 30.0)
        row = self._row(crop, soil, rainfall, temperature, humidity, soil_ph, n, p, k)
        import pandas as pd
        X = pd.DataFrame([row])
        yhat = float(self.model.predict(X)[0])
        return {
            "crop": crop, "soil": soil,
            "predicted_yield_tons_per_ha": round(max(yhat, 0), 3),
            "used_inputs": row,
            "feature_importance": self.feature_importance,
        }

    def recommend_crops(self, soil, rainfall=None, temperature=None, humidity=None,
                          soil_ph=None, n=None, p=None, k=None):
        """Top-3 crops for the farmer's soil + GIVEN parameters (rainfall, temp,
        humidity, pH, N/P/K). Each crop is scored through the trained model using
        these exact parameters (missing ones auto-filled from per-crop real means),
        so the ranking reflects the farmer's actual conditions, not just soil averages.
        """
        results = []
        for crop in self.crops:
            row = self.predict(crop, soil, rainfall=rainfall, temperature=temperature,
                               humidity=humidity, soil_ph=soil_ph, n=n, p=p, k=k)
            results.append((crop, row["predicted_yield_tons_per_ha"]))
        top = sorted(results, key=lambda x: -x[1])[:3]
        return [{"crop": c, "predicted_yield": round(y, 3)} for c, y in top]

    def default_inputs(self, crop="", state=None, lat=None, lon=None):
        # resolve region
        if lat and lon:
            st, _ = gps_to_region(float(lat), float(lon))
            state = st
        # per-state rainfall override
        sw = STATE_WEATHER.get(state, {}) if state else {}
        cd = default_for(crop) if crop else {}
        return {
            "region_state": state,
            "rainfall": sw.get("rainfall", cd.get("rainfall", 1150)),
            "temperature": sw.get("temperature", cd.get("temperature", 27.0)),
            "humidity": sw.get("humidity", cd.get("humidity", 65.0)),
            "soil_ph": cd.get("ph", 6.5),
            "N": cd.get("N", 40.0), "P": cd.get("P", 30.0), "K": cd.get("K", 30.0),
        }
