"""
Flight Fare Prediction (India, 2019) - simple version
Steps: load -> clean -> features -> EDA -> split -> models -> results
Run:   python main.py          (expects data/Data_Train.xlsx)
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # save plots to files, no pop-up windows
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split

SEED = 42                                  # fixed seed = same results every run
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/Data_Train.xlsx")
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- 1. LOAD
if not DATA.exists():
    sys.exit(f"Put Data_Train.xlsx in the data/ folder (not found: {DATA})")
df = pd.read_excel(DATA)
print("1. LOAD")
print("Shape:", df.shape)
print("Missing values:\n", df.isna().sum()[df.isna().sum() > 0])
print("Duplicate rows:", df.duplicated().sum())

# ---------------------------------------------------------------- 2. CLEAN
print("\n2. CLEAN")
n = len(df)
df = df.dropna()                                           # few rows, cannot guess them
df = df.drop_duplicates()                                  # BEFORE splitting, so no copies leak into test
df["Destination"] = df["Destination"].replace("Delhi", "New Delhi")   # same city, two names
df["Additional_Info"] = df["Additional_Info"].str.strip().str.lower() # "No Info" vs "No info"
print(f"Rows: {n} -> {len(df)}")

# ---------------------------------------------------------------- 3. FEATURES
print("\n3. FEATURES")
date = pd.to_datetime(df["Date_of_Journey"], format="%d/%m/%Y")
df["journey_day"] = date.dt.day
df["journey_month"] = date.dt.month
df["dep_hour"] = df["Dep_Time"].astype(str).str[:2].astype(int)       # "22:20"        -> 22
df["arr_hour"] = df["Arrival_Time"].astype(str).str[:2].astype(int)   # "01:10 22 Mar" -> 1
hours = df["Duration"].str.extract(r"(\d+)h")[0].astype(float).fillna(0)     # "2h 50m"
mins = df["Duration"].str.extract(r"(\d+)m")[0].astype(float).fillna(0)
df["duration_min"] = hours * 60 + mins                                       # -> 170
df["stops"] = df["Total_Stops"].map({"non-stop": 0, "1 stop": 1, "2 stops": 2,
                                     "3 stops": 3, "4 stops": 4})
df = df[df["duration_min"] >= 30]                          # impossible durations
df = df.drop(columns=["Date_of_Journey", "Dep_Time", "Arrival_Time",
                      "Duration", "Total_Stops", "Route"])
df["log_price"] = np.log1p(df["Price"])                    # price is skewed -> predict log(price)
print("Features:", [c for c in df.columns if c not in ("Price", "log_price")])
print(f"Price skew: {df['Price'].skew():.2f} -> log skew: {df['log_price'].skew():.2f}")

# ---------------------------------------------------------------- 4. EDA
print("\n4. EDA (plots in outputs/)")
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].hist(df["Price"], bins=50)
ax[0].set_title("Price distribution (INR)")
df.groupby("Airline")["Price"].median().sort_values().plot.barh(ax=ax[1])
ax[1].set_title("Median price by airline")
df.groupby("stops")["Price"].mean().plot.bar(ax=ax[2])
ax[2].set_title("Mean price by stops")
fig.tight_layout()
fig.savefig(OUT / "eda.png", dpi=120)
by_airline = df.groupby("Airline")["Price"].median().sort_values()
print(f"- Mean price {df['Price'].mean():,.0f} vs median {df['Price'].median():,.0f}: right-skewed")
print(f"- Cheapest airline: {by_airline.index[0]}, most expensive: {by_airline.index[-1]}")
print("- Mean price by stops:", df.groupby("stops")["Price"].mean().round(0).to_dict())

# ---------------------------------------------------------------- 5. SPLIT
print("\n5. SPLIT")
categories = ["Airline", "Source", "Destination", "Additional_Info"]
train, test = train_test_split(df, test_size=0.2, random_state=SEED)
features = train.drop(columns=["Price", "log_price"]).columns
# One-hot encode using the TRAIN columns only, then give the test set the same columns
X_train = pd.get_dummies(train[features], columns=categories, drop_first=True, dtype=float)
X_test = pd.get_dummies(test[features], columns=categories, dtype=float)
X_test = X_test.reindex(columns=X_train.columns, fill_value=0.0)
y_train, y_test = train["log_price"], test["log_price"]
print(f"Train: {len(train)} rows, Test: {len(test)} rows, Columns: {X_train.shape[1]}")

# ---------------------------------------------------------------- 6. MODELS
print("\n6. MODELS")
lin = LinearRegression().fit(X_train, y_train)

print("Random Forest: choose max_depth with 5-fold cross-validation (R2 on log price)")
best_depth, best_score = None, -1
for depth in [5, 10, 15]:
    rf = RandomForestRegressor(n_estimators=100, max_depth=depth, random_state=SEED, n_jobs=-1)
    score = cross_val_score(rf, X_train, y_train, cv=5, scoring="r2").mean()
    print(f"  max_depth={depth:2d}  CV R2 = {score:.3f}")
    if score > best_score:
        best_depth, best_score = depth, score
forest = RandomForestRegressor(n_estimators=200, max_depth=best_depth,
                               random_state=SEED, n_jobs=-1).fit(X_train, y_train)
print("Best max_depth:", best_depth)
print(f"Linear Regression CV R2 = {cross_val_score(LinearRegression(), X_train, y_train, cv=5, scoring='r2').mean():.3f}")

# ---------------------------------------------------------------- 7. RESULTS
print("\n7. RESULTS ON TEST SET (errors in INR)")
actual = test["Price"].values
preds = {
    "Baseline (mean)": np.full(len(test), train["Price"].mean()),
    "Linear Regression": np.expm1(lin.predict(X_test)),     # back from log to rupees
    "Random Forest": np.expm1(forest.predict(X_test)),
}
rows = []
for name, p in preds.items():
    rows.append({"model": name,
                 "RMSE": np.sqrt(mean_squared_error(actual, p)),
                 "MAE": mean_absolute_error(actual, p),
                 "R2": r2_score(actual, p)})
results = pd.DataFrame(rows)
print(results.to_string(index=False, float_format="%.2f"))
results.to_csv(OUT / "results.csv", index=False)

# ---------------------------------------------------------------- 8. UNDERSTAND
print("\n8. WHAT DRIVES PRICE?")
coef = pd.Series(lin.coef_, index=X_train.columns)
print("Linear Regression: 5 biggest effects (on log price, so exp(coef)-1 = % change)")
for name, c in coef.reindex(coef.abs().sort_values(ascending=False).index).head(5).items():
    print(f"  {name:35s} {100 * (np.exp(c) - 1):+8.1f}%")
imp = pd.Series(forest.feature_importances_, index=X_train.columns).sort_values(ascending=False)
print("Random Forest: 5 most important features")
for name, v in imp.head(5).items():
    print(f"  {name:35s} {v:.3f}")

print("\nError analysis (Random Forest, average error by airline, INR):")
err = pd.DataFrame({"Airline": test["Airline"].values, "error": np.abs(actual - preds["Random Forest"])})
print(err.groupby("Airline")["error"].agg(["count", "mean"]).round(0).sort_values("mean", ascending=False).to_string())

fig, ax = plt.subplots(figsize=(5, 5))
ax.scatter(actual, preds["Random Forest"], s=5, alpha=0.4)
ax.plot([0, actual.max()], [0, actual.max()], color="red")
ax.set_xlabel("Actual price")
ax.set_ylabel("Predicted price")
ax.set_title("Random Forest: actual vs predicted (test)")
fig.tight_layout()
fig.savefig(OUT / "actual_vs_predicted.png", dpi=120)
print("\nDone. Saved outputs/eda.png, outputs/actual_vs_predicted.png, outputs/results.csv")
