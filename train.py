"""train.py — benchmark 7 regression models on the REAL cleaned dataset,
compute permutation importance, save best (KNN) model + meta.
"""
import pandas as pd, numpy as np, joblib, json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.inspection import permutation_importance

RANDOM = 42
SAMPLE_CAP = 40000  # cap for reasonable runtime on real data

df = pd.read_csv("data/crop_yield.csv")
if len(df) > SAMPLE_CAP:
    df = df.sample(SAMPLE_CAP, random_state=RANDOM).reset_index(drop=True)

df = df.dropna()
TARGET = "Yield_tons_per_ha"
cat = ["Crop", "Soil_Type"]
num = ["Rainfall", "Temperature", "Humidity", "Soil_pH", "N", "P", "K"]

X = df[cat + num]
y = df[TARGET].values

pre = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ("num", StandardScaler(), num),
])

models = {
    "LinearRegression": LinearRegression(),
    "DecisionTree": DecisionTreeRegressor(random_state=RANDOM),
    "RandomForest": RandomForestRegressor(n_estimators=120, random_state=RANDOM, n_jobs=-1),
    "GradientBoosting": GradientBoostingRegressor(random_state=RANDOM),
    "KNeighbors": KNeighborsRegressor(n_neighbors=5, n_jobs=-1),
    "SVR": SVR(),
    "XGBoost": None,  # filled below if available
}
# try xgboost
try:
    from xgboost import XGBRegressor
    models["XGBoost"] = XGBRegressor(n_estimators=120, random_state=RANDOM, verbosity=0)
except Exception:
    pass

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=RANDOM)

results = {}
fitted = {}
for name, m in models.items():
    if m is None:
        continue
    pipe = Pipeline([("pre", pre), ("est", m)])
    pipe.fit(X_tr, y_tr)
    pred = pipe.predict(X_te)
    r2 = r2_score(y_te, pred)
    mae = mean_absolute_error(y_te, pred)
    rmse = mean_squared_error(y_te, pred) ** 0.5
    results[name] = {"R2": round(r2, 4), "MAE": round(mae, 3), "RMSE": round(rmse, 3)}
    fitted[name] = pipe
    print(f"{name:18s} R2={r2:.4f}  MAE={mae:.3f}  RMSE={rmse:.3f}")

best = max(results, key=lambda k: results[k]["R2"])
print("\nBEST:", best, results[best])

# permutation importance on best
best_pipe = fitted[best]
perm = permutation_importance(best_pipe, X_te, y_te, n_repeats=5, random_state=RANDOM, n_jobs=-1)
feat_names = list(X.columns)
importances = sorted(zip(feat_names, perm.importances_mean), key=lambda x: -x[1])

# meta
meta = {
    "best_model": best,
    "metrics": results[best],
    "all_metrics": results,
    "crops": sorted(df["Crop"].unique().tolist()),
    "soils": sorted(df["Soil_Type"].unique().tolist()),
    "feature_importance": {k: float(v) for k, v in importances},
    "n_rows": int(len(df)),
    "target": TARGET,
}

joblib.dump(best_pipe, "model/yield_model.pkl")
joblib.dump(meta, "model/meta.pkl")
print("\nSaved model/yield_model.pkl (", best, ") + model/meta.pkl")
print("Feature importance:")
for k, v in importances:
    print(f"  {k:14s} {v:.2f}")
