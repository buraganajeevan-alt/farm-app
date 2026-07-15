"""
predict_helper.py
-----------------
Loads the trained model + encoders and makes a prediction with
suitability check, confidence estimate, and yield-improvement suggestions.
"""
import os
import joblib
import numpy as np
from crop_defaults import default_inputs as _crop_defaults

MODEL_DIR = "model"


class Predictor:
    def __init__(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, "yield_model.pkl"))
        self.le_crop = joblib.load(os.path.join(MODEL_DIR, "crop_encoder.pkl"))
        self.le_soil = joblib.load(os.path.join(MODEL_DIR, "soil_encoder.pkl"))
        self.meta = joblib.load(os.path.join(MODEL_DIR, "meta.pkl"))
        self.feature_cols = self.meta["feature_cols"]

    def default_inputs(self, crop_name):
        """Regional/typical defaults for a crop (farmer need not measure these)."""
        return _crop_defaults(crop_name)

    def _safe_encode(self, le, value, default_idx=0):
        try:
            return le.transform([value])[0]
        except ValueError:
            return default_idx

    def predict(self, data):
        """
        data: dict with keys Crop, Soil_Type, Rainfall, Temperature,
              Humidity, pH, N, P, K (numbers as float/int, strings for crop/soil)
        Returns dict: predicted_yield, suitable (bool), confidence,
                      suggestions (list), model_name
        """
        crop_enc = self._safe_encode(self.le_crop, data["Crop"])
        soil_enc = self._safe_encode(self.le_soil, data["Soil_Type"])

        features = np.array([[
            crop_enc, soil_enc,
            float(data["Rainfall"]), float(data["Temperature"]),
            float(data["Humidity"]), float(data["pH"]),
            float(data["N"]), float(data["P"]), float(data["K"])
        ]])
        # build DataFrame with feature names to match training
        import pandas as pd
        X = pd.DataFrame([dict(zip(self.feature_cols, features[0]))],
                         columns=self.feature_cols)

        pred = float(self.model.predict(X)[0])
        pred = max(0.0, round(pred, 3))

        # ---- suitability heuristic ----
        # Is the soil in the crop's known suitable list? We derive "known"
        # from training classes: if crop and soil co-occur frequently -> suitable.
        # Simple, explainable rule using pH + soil match knowledge:
        suitable = self._suitability(data)

        # ---- confidence ----
        # Use training RMSE as base uncertainty; tighten if conditions are
        # within typical agronomic ranges.
        base_rmse = self.meta["metrics"][self.meta["best_model"]]["rmse"]
        # crude confidence: higher when inputs are in plausible ranges
        conf = self._confidence(data, base_rmse)

        # ---- suggestions ----
        suggestions = self._suggestions(data, suitable)

        return {
            "predicted_yield": pred,
            "suitable": suitable,
            "confidence": round(conf, 2),
            "suggestions": suggestions,
            "model_name": self.meta["best_model"],
        }

    def recommend_crops(self, data, top_n=3):
        """
        Given soil + environmental conditions (Rainfall, Temperature,
        Humidity, pH, N, P, K), predict the yield each known crop would
        give and return the top `top_n` crops with highest predicted yield.

        data must contain: Soil_Type, Rainfall, Temperature, Humidity,
        pH, N, P, K  (Crop is ignored / swept over all crops).
        Returns list of dicts: [{crop, predicted_yield, suitable}, ...]
        """
        import pandas as pd
        results = []
        for crop in self.meta["crops"]:
            trial = {
                "Crop": crop,
                "Soil_Type": data["Soil_Type"],
                "Rainfall": data["Rainfall"],
                "Temperature": data["Temperature"],
                "Humidity": data["Humidity"],
                "pH": data["pH"],
                "N": data["N"],
                "P": data["P"],
                "K": data["K"],
            }
            crop_enc = self._safe_encode(self.le_crop, crop)
            soil_enc = self._safe_encode(self.le_soil, data["Soil_Type"])
            feat = np.array([[
                crop_enc, soil_enc,
                float(data["Rainfall"]), float(data["Temperature"]),
                float(data["Humidity"]), float(data["pH"]),
                float(data["N"]), float(data["P"]), float(data["K"])
            ]])
            X = pd.DataFrame([dict(zip(self.feature_cols, feat[0]))],
                             columns=self.feature_cols)
            y = max(0.0, round(float(self.model.predict(X)[0]), 3))
            results.append({
                "crop": crop,
                "predicted_yield": y,
                "suitable": self._suitability(trial),
            })
        # sort by predicted yield, highest first
        results.sort(key=lambda r: r["predicted_yield"], reverse=True)
        return results[:top_n]

    def _suitability(self, d):
        # Agronomic compatibility table (subset; expandable)
        compat = {
            "Rice": ["Clay", "Alluvial", "Loamy"],
            "Wheat": ["Loamy", "Clay", "Alluvial"],
            "Maize": ["Loamy", "Silt", "Alluvial"],
            "Cotton": ["Black", "Loamy", "Red"],
            "Sugarcane": ["Loamy", "Alluvial", "Black"],
            "Soybean": ["Loamy", "Silt", "Black"],
            "Groundnut": ["Sandy", "Loamy", "Red"],
            "Millet": ["Sandy", "Red", "Loamy"],
            "Banana": ["Loamy", "Alluvial", "Silt"],
            "Tomato": ["Loamy", "Silt", "Alluvial"],
        }
        ok_soils = compat.get(d["Crop"], [])
        soil_ok = (not ok_soils) or (d["Soil_Type"] in ok_soils)
        # pH plausibility per crop (loose)
        ph_ok = 5.0 <= d["pH"] <= 8.5
        return soil_ok and ph_ok

    def _confidence(self, d, base_rmse):
        # map RMSE (absolute error) to a 0-100-ish confidence.
        # Lower relative error -> higher confidence.
        typical_yield = 10.0  # scaling constant for interpretability
        rel = base_rmse / (typical_yield + 1e-6)
        conf = max(0.3, 1.0 - rel)
        # small boost if inputs are in common ranges
        if 50 <= d["Rainfall"] <= 300 and 15 <= d["Temperature"] <= 35:
            conf = min(0.98, conf + 0.05)
        return min(0.99, conf)

    def _suggestions(self, d, suitable):
        s = []
        if not suitable:
            s.append(
                f"{d['Crop']} is not ideally grown on {d['Soil_Type']} soil. "
                f"Consider a more compatible soil/crop pairing.")
        if d["pH"] < 6.0:
            s.append("Soil is acidic (pH < 6). Add agricultural lime to raise pH.")
        elif d["pH"] > 7.5:
            s.append("Soil is alkaline (pH > 7.5). Use acidifying amendments (e.g., gypsum/sulfur) or choose tolerant crops.")
        if d["N"] < 40:
            s.append("Low Nitrogen. Apply urea or organic manure to boost vegetative growth.")
        if d["P"] < 25:
            s.append("Low Phosphorus. Add single super phosphate (SSP) or bone meal.")
        if d["K"] < 25:
            s.append("Low Potassium. Apply muriate of potash (MOP) for better grain/fruit quality.")
        if d["Rainfall"] < 60:
            s.append("Low rainfall. Consider drip irrigation or drought-tolerant varieties.")
        elif d["Rainfall"] > 250:
            s.append("Very high rainfall. Ensure drainage to avoid waterlogging.")
        if not s:
            s.append("Conditions look good. Maintain soil health with crop rotation and organic matter.")
        return s
