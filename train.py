"""
train.py
--------
Smart Farming - AI Based Crop Yield Prediction

Pipeline:
  1. Load dataset (data/crop_yield.csv)
  2. Clean data
  3. Encode categorical features (Crop, Soil_Type)
  4. Train multiple regression models
  5. Compare accuracy (R^2, MAE, RMSE)
  6. Save the best model + encoders + metrics + feature list

Run:  python train.py
"""
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

DATA_PATH = os.path.join("data", "crop_yield.csv")
MODEL_DIR = "model"
TARGET = "Yield"

# ---------------------------------------------------------------- load + clean
def load_and_clean(path):
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns")

    # drop rows with missing critical values
    df = df.dropna(subset=[TARGET])
    # numeric coercion
    num_cols = ["Rainfall", "Temperature", "Humidity", "pH", "N", "P", "K", "Yield"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna()
    # remove impossible values
    df = df[(df[TARGET] > 0) & (df["pH"].between(3, 10))]
    df = df.reset_index(drop=True)
    print(f"After cleaning: {len(df)} rows")
    return df


# ---------------------------------------------------------------- encode
def encode(df):
    le_crop = LabelEncoder()
    le_soil = LabelEncoder()
    df["Crop_enc"] = le_crop.fit_transform(df["Crop"])
    df["Soil_enc"] = le_soil.fit_transform(df["Soil_Type"])
    return df, le_crop, le_soil


# ---------------------------------------------------------------- main
def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = load_and_clean(DATA_PATH)
    # Cap sample size for reasonable training time (data remains REAL).
    MAX_ROWS = 40000
    if len(df) > MAX_ROWS:
        df = df.sample(MAX_ROWS, random_state=42).reset_index(drop=True)
        print(f"Sampled to {MAX_ROWS} rows for training.")
    df, le_crop, le_soil = encode(df)

    feature_cols = ["Crop_enc", "Soil_enc", "Rainfall", "Temperature",
                    "Humidity", "pH", "N", "P", "K"]
    X = df[feature_cols]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
        "KNN": KNeighborsRegressor(n_neighbors=5),
    }
    # SVR does not scale to large samples; include only on small data.
    if len(X_train) <= 8000:
        models["SVR"] = SVR(kernel="rbf")

    if XGB_AVAILABLE:
        models["XGBoost"] = XGBRegressor(
            n_estimators=200, learning_rate=0.1, random_state=42,
            n_jobs=-1, verbosity=0)
    else:
        print("WARNING: xgboost not installed, skipping XGBoost model.")

    results = {}
    print("\n%-22s %8s %10s %10s" % ("Model", "R2", "MAE", "RMSE"))
    print("-" * 56)
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        r2 = r2_score(y_test, pred)
        mae = mean_absolute_error(y_test, pred)
        rmse = mean_squared_error(y_test, pred) ** 0.5
        results[name] = (r2, mae, rmse)
        print("%-22s %8.3f %10.3f %10.3f" % (name, r2, mae, rmse))

    # pick best by R2
    best_name = max(results, key=lambda k: results[k][0])
    best_model = models[best_name]
    print(f"\nBest model: {best_name}  (R2 = {results[best_name][0]:.3f})")

    # ---- explainable feature importance (permutation) on best model ----
    from sklearn.inspection import permutation_importance
    perm = permutation_importance(
        best_model, X_test, y_test, n_repeats=5,
        random_state=42, scoring="neg_root_mean_squared_error", n_jobs=-1)
    importance = {feature_cols[i]: float(perm.importances_mean[i])
                   for i in range(len(feature_cols))}
    importance = dict(sorted(importance.items(),
                            key=lambda kv: kv[1], reverse=True))
    print("\nPermutation importance (RMSE increase when shuffled):")
    for k, v in importance.items():
        print(f"  {k:14s} {v:.3f}")

    # save artifacts
    joblib.dump(best_model, os.path.join(MODEL_DIR, "yield_model.pkl"))
    joblib.dump(le_crop, os.path.join(MODEL_DIR, "crop_encoder.pkl"))
    joblib.dump(le_soil, os.path.join(MODEL_DIR, "soil_encoder.pkl"))
    meta = {
        "feature_cols": feature_cols,
        "best_model": best_name,
        "metrics": {k: {"r2": v[0], "mae": v[1], "rmse": v[2]} for k, v in results.items()},
        "permutation_importance": importance,
        "crops": list(le_crop.classes_),
        "soils": list(le_soil.classes_),
    }
    joblib.dump(meta, os.path.join(MODEL_DIR, "meta.pkl"))
    print(f"Artifacts saved to ./{MODEL_DIR}/")


if __name__ == "__main__":
    main()
