import pandas as pd
import numpy as np
import re
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

# Load the dataset
df = pd.read_csv("updated_with_coefficients.csv")

# Define element columns
element_cols = [
    "O", "N", "C", "B", "Si", "Al", "Mg", "Zr", "Ti", "Ca", "Y", "Hf", "Fe", "Na",
    "K","Ba", "Sr", "Li", "Be", "Mn", "V", "Cr", "Nb", "Mo", "W", "Re",
    "Sc", "La", "Ce", "Th", "U"
]

# Input features
input_features = ["Bulk Modulus", "Shear Modulus", "Tm"]
X = df[input_features]

# Output features (excluding inputs and identifiers)
output_features = [
    col for col in df.columns
    if col not in input_features + ["Formula", "Elements"]
]

# Include the Formula column separately for post-processing
y = df[output_features + ["Formula"]].copy()

# Train the model using Ridge Regressor
ridge = Ridge(alpha=1.0)
model = MultiOutputRegressor(ridge)
model.fit(X, y[output_features])

# Evaluate
y_pred = model.predict(X)
r2 = r2_score(y[output_features], y_pred)
mae = mean_absolute_error(y[output_features], y_pred)
print("R2:", r2)
print("MAE:", mae)

# Save model
joblib.dump(model, "ridge_composition_predictor.pkl")

# Predict from an example input
example_input = pd.DataFrame.from_dict([{
    "Bulk Modulus": 150,
    "Shear Modulus": 80,
    "Tm": 1800
}])

predicted_values = model.predict(example_input)[0]

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
