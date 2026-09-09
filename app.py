"""app.py — Flask web app for the Smart Farming crop-yield project.
Farmer-practical: only Crop + Soil Type required.
GPS button OR State dropdown resolves region -> real IMD rainfall auto-fill.
Soil Health Card (pH/N/P/K) auto-fills from real per-crop means, overridable.
"""
from flask import Flask, request, jsonify, render_template, session
from predict_helper import Predictor
from geo_state import resolve_region, STATE_WEATHER
try:
    from dotenv import load_dotenv
    load_dotenv()  # load GROQ_API_KEY etc. from .env if present
except Exception:
    pass
from agri_chat import chat as agri_chat, is_available as chat_available, transcribe as agri_transcribe, speak as agri_speak, diagnose as agri_diagnose

app = Flask(__name__)
app.secret_key = "smart-farming-dev-key"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
predictor = Predictor()

CROPS = predictor.meta["crops"]
SOILS = predictor.meta["soils"]
STATES = sorted(STATE_WEATHER.keys())

def _f(v):
    try: return float(v)
    except: return None

@app.route("/")
def home():
    return render_template("index.html", crops=CROPS, soils=SOILS, states=STATES,
                           best=predictor.meta["best_model"],
                           metrics=predictor.meta["metrics"])

@app.route("/api/geo", methods=["POST"])
def api_geo():
    try:
        body = request.get_json(force=True, silent=True) or {}
        lat = float(body.get("lat")); lon = float(body.get("lon"))
        rg = resolve_region(lat, lon)
        msg = rg["message"]
        if rg.get("district_mean_yield"):
            msg += f"  ·  district mean yield ≈ {rg['district_mean_yield']:.2f} t/ha"
        return jsonify({"state": rg["state"], "district": rg.get("district"),
                       "tier": rg["tier"], "rainfall": rg["rainfall"],
                       "district_mean_yield": rg.get("district_mean_yield"),
                       "message": msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/geo/search", methods=["GET"])
def api_geo_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])
    from geo_state import search_location_places
    places = search_location_places(q)
    return jsonify(places)

@app.route("/api/state", methods=["POST"])
def api_state():
    body = request.get_json(force=True, silent=True) or {}
    st = body.get("state")
    rf = STATE_WEATHER.get(st, {}).get("rainfall", 1150)
    return jsonify({"state": st, "rainfall": rf,
                   "message": f"{st}: rainfall {rf} mm (IMD)"})

@app.route("/api/predict", methods=["POST"])
def api_predict():
    f = request.form if request.form else (request.get_json(force=True, silent=True) or {})
    crop = f.get("crop"); soil = f.get("soil")
    if not crop or not soil:
        return jsonify({"error": "Crop and Soil Type are required."}), 400
    res = predictor.predict(crop, soil,
                            rainfall=_f(f.get("rainfall")),
                            temperature=_f(f.get("temperature")),
                            humidity=_f(f.get("humidity")),
                            soil_ph=_f(f.get("soil_ph")),
                            n=_f(f.get("n")), p=_f(f.get("p")), k=_f(f.get("k")))
    return jsonify(res)

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    f = request.form if request.form else (request.get_json(force=True, silent=True) or {})
    soil = f.get("soil") or (f.get("soil_type"))
    if not soil:
        return jsonify({"error": "Soil Type is required for recommendation."}), 400
    return jsonify({"soil": soil, "top3": predictor.recommend_crops(
        soil, rainfall=_f(f.get("rainfall")), temperature=_f(f.get("temperature")),
        humidity=_f(f.get("humidity")), soil_ph=_f(f.get("soil_ph")),
        n=_f(f.get("n")), p=_f(f.get("p")), k=_f(f.get("k")))})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = request.get_json(force=True, silent=True) or {}
    msg = (body.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Empty message."}), 400
    history = session.get("chat_history", [])
    farm_context = body.get("farm_context") or session.get("last_farm_context") or {}
    lang = body.get("lang") or "te"
    reply, status, audio = agri_chat(msg, history=history, speak_lang=lang, farm_context=farm_context)
    if status in ["ok", "ok_fallback"]:
        history.append({"user": msg, "ai": reply})
        session["chat_history"] = history[-8:]
    return jsonify({"reply": reply, "status": status,
                    "available": chat_available(), "audio": audio})

@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    session["chat_history"] = []
    return jsonify({"ok": True})

@app.route("/api/chat/transcribe", methods=["POST"])
def api_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file."}), 400
    f = request.files["audio"]
    data = f.read()
    lang = request.form.get("lang") or None
    text, status = agri_transcribe(data, f.filename or "audio.webm", lang=lang)
    return jsonify({"text": text, "status": status})

@app.route("/api/chat/speak", methods=["POST"])
def api_speak():
    body = request.get_json(force=True, silent=True) or {}
    text = (body.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Empty text."}), 400
    b64, status = agri_speak(text, body.get("lang", "te"))
    return jsonify({"audio": b64, "status": status})

@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():
    if "image" not in request.files:
        return jsonify({"error": "No image file."}), 400
    f = request.files["image"]
    data = f.read()
    result, status = agri_diagnose(data, f.filename or "image.jpg")
    return jsonify({"result": result, "status": status})

@app.route("/api/rag/search", methods=["POST"])
def api_rag_search():
    body = request.get_json(force=True, silent=True) or {}
    q = (body.get("query") or "").strip()
    if not q:
        return jsonify({"error": "Empty query."}), 400
    import agri_rag
    results, context = agri_rag.retrieve(q, top_k=int(body.get("top_k", 3)))
    return jsonify({"results": results, "context": context, "count": len(results)})

@app.route("/api/weather/3day", methods=["GET", "POST"])
def api_weather_3day():
    if request.method == "POST":
        body = request.get_json(force=True, silent=True) or {}
        lat = body.get("lat")
        lon = body.get("lon")
        state = body.get("state")
    else:
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        state = request.args.get("state")
    
    import weather_service
    forecast_data = weather_service.get_3day_weather(lat=lat, lon=lon, state_name=state)
    return jsonify(forecast_data)

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
