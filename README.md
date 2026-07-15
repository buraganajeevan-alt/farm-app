# Smart Farming — AI Based Crop Yield Prediction

An AI-powered web application that predicts **crop yield (kg/hectare)** from
crop name, soil type, and (optionally) rainfall, temperature, humidity, pH,
and NPK values. It also reports whether the crop is **suitable** for the soil,
a **confidence** score, and **suggestions** to improve yield.

## Project Structure
```
smart_farming/
├── generate_dataset.py   # creates synthetic data (replace with real data)
├── train.py              # cleans data, trains 6 ML models, saves best
├── predict_helper.py     # loads model + makes predictions + suggestions
├── app.py               # Flask web server
├── templates/
│   └── index.html       # farmer-friendly form UI
├── data/
│   └── crop_yield.csv   # dataset (10 columns)
└── model/               # saved model + encoders + metrics (auto-created)
```

## Setup
```bash
# use the Python that has the packages (Windows example)
pip install pandas scikit-learn flask numpy joblib

# 1. generate the dataset
python generate_dataset.py

# 2. train the model (compares 6 algorithms, saves the best)
python train.py

# 3. run the web app
python app.py
```
Then open **http://127.0.0.1:5000** in your browser.

## How It Works
1. **Collect / Prepare data** — `data/crop_yield.csv` (Crop, Soil_Type,
   Rainfall, Temperature, Humidity, pH, N, P, K, Yield).
2. **Clean data** — drop missing/impossible values, coerce numerics.
3. **Train multiple models** — Linear Regression, Decision Tree, Random
   Forest, Gradient Boosting, SVR, KNN.
4. **Compare accuracy** — R², MAE, RMSE on a held-out test set.
5. **Save the best model** — serialized with `joblib`.
6. **Flask app** — farmer enters details → model predicts yield →
   suitability, confidence, and improvement suggestions are shown.

## Dataset (REAL, not synthetic)
`data/crop_yield.csv` is built from a real, public Indian agriculture
dataset (241,226 raw records; 186,323 cleaned rows; 104 crops) with
MEASURED yield (Production/Area, t/ha), Soil Type, Soil pH, and
annual rainfall. Source: "Crop Yield Prediction" dataset (GitHub,
punitkumar4871). Temperature/Humidity/N/P/K are filled from the real
"Crop Recommendation" dataset's per-crop agronomic means (those four
fields are not in the yield source). See TERM_PAPER_NOTES.md §0.

To rebuild: `python build_from_real_yield.py` (needs realdata/real_yield_dataset.csv
+ realdata/crop_recommendation.csv, already downloaded).
To use your own data: replace `data/crop_yield.csv` keeping the same 10
column headers and re-run `train.py` — no code changes needed.

## API (for integration)
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"Crop":"Rice","Soil_Type":"Clay","Rainfall":200,"Temperature":27,
       "Humidity":80,"pH":6.2,"N":100,"P":50,"K":40}'
```
