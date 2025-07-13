import pandas as pd
import numpy as np
import re
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

# Load the dataset
df = pd.read_csv("updated_with_coefficients.csv")

# Define element columns
element_cols = [
    "O", "N", "C", "B", "Si", "Al", "Mg", "Zr", "Ti", "Ca", "Y", "Hf", "Fe", "Na",
    "K", "Ba", "Sr", "Li", "Be", "Mn", "V", "Cr", "Nb", "Mo", "W", "Re",
    "Sc", "La", "Ce", "Th", "U"
]

# Input features (same as LinearRegression version)
input_features = ["Bulk Modulus", "Shear Modulus", "Tm"]
X = df[input_features]

# Output features (excluding inputs and identifiers)
output_features = [
    col for col in df.columns
    if col not in input_features + ["Formula", "Elements"]
]

# Include the Formula column separately for post-processing
y = df[output_features].copy()

# 5-Fold Cross-Validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
fold_scores = []
fold_maes = []

for fold, (train_idx, test_idx) in enumerate(kf.split(X)):
    print(f"Fold {fold + 1}")
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[output_features].iloc[train_idx], y[output_features].iloc[test_idx]

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    fold_scores.append(score)
    fold_maes.append(mae)
    
    print(f"R² score: {score:.3f}")
    print(f"MAE: {mae:.3f}")

# Report average score
print(f"\nAverage R² across folds: {np.mean(fold_scores):.3f}")
print(f"Average MAE across folds: {np.mean(fold_maes):.3f}")

# Train final model on full dataset
final_model = RandomForestRegressor(n_estimators=200, random_state=42)
final_model.fit(X, y[output_features])

# Evaluate on full dataset
y_pred_full = final_model.predict(X)
r2 = r2_score(y[output_features], y_pred_full)
mae = mean_absolute_error(y[output_features], y_pred_full)
print(f"\nFull dataset performance:")
print("R2:", r2)
print("MAE:", mae)

# Save model
joblib.dump(final_model, "composition_predictor.pkl")
print("Final model saved to composition_predictor.pkl")

# Predict from an example input
example_input = pd.DataFrame.from_dict([{
    "Bulk Modulus": 150,
    "Shear Modulus": 80,
    "Tm": 1800
}])

predicted_values = final_model.predict(example_input)[0]

# Format output
predicted_dict = dict(zip(output_features, predicted_values))

# Extract element counts for formula
predicted_elements = {
    el: round(predicted_dict[el]) for el in element_cols
    if predicted_dict[el] > 0.05
}

# Construct formula
formula = "".join(
    f"{el}{int(count)}" if count > 1 else f"{el}"
    for el, count in predicted_elements.items()
)

predicted_dict["Predicted_Formula"] = formula

# Show final prediction
print("\nPredicted Properties:")
for k, v in predicted_dict.items():
    print(f"{k}: {v}")