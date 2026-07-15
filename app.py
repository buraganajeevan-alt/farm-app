"""
app.py — Smart Farming AI Crop Yield Prediction (farmer-practical build)
----------------------------------------------------------------
Design (per deployment discussion):
  - Farmer enters ONLY what they know: Crop + Soil Type.
  - Rainfall / Temperature / Humidity / pH / N / P / K AUTO-FILL
    from REAL regional/typical per-crop defaults (stand-in for government
    open data: IMD, Soil Health Card, NBSS&LUP).
  - Farmer MAY override any field with their OWN soil-test values
    (e.g. their Soil Health Card numbers) for a sharper prediction.
  - Yield is the model's OUTPUT, never an input.
  - '/recommend' ranks all crops by predicted yield for the soil profile.
"""
import os
from flask import Flask, render_template, request, jsonify

from predict_helper import Predictor
from geo_state import gps_to_region, STATE_WEATHER
from shc_helper import lookup as lookup_shc

app = Flask(__name__)
predictor = Predictor()

CROPS = predictor.meta["crops"]
SOILS = predictor.meta["soils"]
STATES = sorted(STATE_WEATHER.keys())  # real state codes w/ rainfall defaults

# fields a farmer does NOT need to measure (auto-filled, overridable)
AUTO_FIELDS = ["rainfall", "temperature", "humidity", "ph", "n", "p", "k"]


@app.route("/api/geo", methods=["POST"])
def api_geo():
    try:
        lat = float(request.get_json(force=True).get("lat"))
        lon = float(request.get_json(force=True).get("lon"))
        region = gps_to_region(lat, lon)
        return jsonify({"status": "ok", **region})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/shc", methods=["POST"])
def api_shc():
    try:
        shc_id = request.get_json(force=True).get("shc_id", "")
        rec = lookup_shc(shc_id)
        return jsonify(rec)
    except Exception as e:
        return jsonify({"found": False, "error": str(e)}), 400


@app.route("/api/state", methods=["POST"])
def api_state():
    try:
        code = request.get_json(force=True).get("state")
        rain = STATE_WEATHER.get(code, {}).get("rain", 200.0)
        return jsonify({"status": "ok", "state_code": code,
                     "rainfall_default": rain})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


def build_data(form):
    """Build the prediction dict. Crop+Soil required; rest defaulted
    from real per-crop values, or from the farmer's selected STATE
    rainfall if they picked one, unless they typed their own.
    If a valid Soil Health Card (SHC) ID is supplied, its pH/N/P/K
    values are used as the base defaults (overridable by manual entry)."""
    crop = form.get("crop")
    soil = form.get("soil")
    state = (form.get("state") or "").strip()
    data = {"Crop": crop, "Soil_Type": soil}
    defaults = predictor.default_inputs(crop) if crop else {}
    # state-level rainfall overrides the generic per-crop rainfall default
    if state and state in STATE_WEATHER:
        defaults = dict(defaults)
        defaults["Rainfall"] = STATE_WEATHER[state]["rain"]
    # Soil Health Card: if a valid SHC ID is given, its plot-specific
    # pH/N/P/K replaces the regional default (unless farmer types their own).
    shc_id = (form.get("shc_id") or "").strip()
    if shc_id:
        rec = lookup_shc(shc_id)
        if rec.get("found"):
            defaults = dict(defaults)
            for dkey, rkey in [("pH", "ph"), ("N", "n"), ("P", "p"), ("K", "k")]:
                if rec.get(rkey) is not None:
                    defaults[dkey] = rec[rkey]
    keymap = {"rainfall": "Rainfall", "temperature": "Temperature",
               "humidity": "Humidity", "ph": "pH", "n": "N",
               "p": "P", "k": "K"}
    for fname, dkey in keymap.items():
        raw = form.get(fname, "").strip()
        if raw != "":                      # farmer supplied their own value
            data[dkey] = float(raw)
        else:                             # auto-fill regional default
            data[dkey] = float(defaults.get(dkey, 0))
    return data, defaults


@app.route("/")
def home():
    return render_template("index.html", crops=CROPS, soils=SOILS,
                          model_name=predictor.meta["best_model"],
                          auto_fields=AUTO_FIELDS, states=STATES,
                          shc_id="")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data, defaults = build_data(request.form)
        result = predictor.predict(data)
        result["defaults_used"] = {
            k: v for k, v in defaults.items()
            if request.form.get(k.lower(), "").strip() == ""}
        return render_template("index.html", crops=CROPS, soils=SOILS,
                               model_name=predictor.meta["best_model"],
                               result=result, input_data=data,
                               auto_fields=AUTO_FIELDS, states=STATES,
                               shc_id=(request.form.get("shc_id") or "").strip())
    except Exception as e:
        return render_template("index.html", crops=CROPS, soils=SOILS,
                               model_name=predictor.meta["best_model"],
                               error=str(e), auto_fields=AUTO_FIELDS,
                               shc_id=(request.form.get("shc_id") or "").strip())


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data, _ = build_data(request.form)
        data.pop("Crop", None)
        recs = predictor.recommend_crops(data, top_n=3)
        return render_template("index.html", crops=CROPS, soils=SOILS,
                               model_name=predictor.meta["best_model"],
                               recommendations=recs, input_data=data,
                               auto_fields=AUTO_FIELDS, states=STATES,
                               shc_id=(request.form.get("shc_id") or "").strip())
    except Exception as e:
        return render_template("index.html", crops=CROPS, soils=SOILS,
                               model_name=predictor.meta["best_model"],
                               error=str(e), auto_fields=AUTO_FIELDS,
                               shc_id=(request.form.get("shc_id") or "").strip())


@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json(force=True)
        # allow partial: fill missing from defaults
        crop = data.get("Crop")
        defaults = predictor.default_inputs(crop) if crop else {}
        for k in ["Rainfall", "Temperature", "Humidity", "pH", "N", "P", "K"]:
            if k not in data or data[k] in (None, ""):
                data[k] = defaults.get(k, 0)
        result = predictor.predict(data)
        return jsonify({"status": "ok", **result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    try:
        data = request.get_json(force=True)
        defaults = predictor.default_inputs(data.get("Crop")) if data.get("Crop") else {}
        for k in ["Rainfall", "Temperature", "Humidity", "pH", "N", "P", "K"]:
            if k not in data or data[k] in (None, ""):
                data[k] = defaults.get(k, 0)
        data.pop("Crop", None)
        recs = predictor.recommend_crops(data, top_n=3)
        return jsonify({"status": "ok", "recommendations": recs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
