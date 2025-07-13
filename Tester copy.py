import pandas as pd
import numpy as np
import joblib
import re
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error

# === 1. Load the trained model ===
model = joblib.load("gb_composition_predictor.pkl")  # Ensure this .pkl file is in the same folder

# === 2. Load the dataset ===
df = pd.read_csv("test_data.csv")

# === 3. Define input features (must match model training) ===
element_cols = ["O", "N", "C", "B", "Si", "Al", "Mg", "Zr", "Ti", "Ca", "Y", "Hf", "Fe", "Na",
                "K", "P", "S", "Ba", "Sr", "Li", "Be", "Mn", "V", "Cr", "Nb", "Mo", "W", "Re",
                "Sc", "La", "Ce", "Th", "U"]
input_features = ["Bulk Modulus", "Shear Modulus", "Tm"]
output_features = [
    col for col in df.columns
    if col not in input_features + ["Formula", "Elements"]
]
X = df[input_features]

# === 4. Parse the Formula column to get actual compositions ===
def parse_formula(formula):
    tokens = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', str(formula))
    return {el: float(count) if count else 1.0 for el, count in tokens}

parsed = df["Formula"].apply(parse_formula)
all_elements = sorted({el for f in parsed for el in f})
y_actual = pd.DataFrame([{el: f.get(el, 0.0) for el in all_elements} for f in parsed])

# === 5. Predict using the model ===
y_pred = model.predict(X)
y_pred_df = pd.DataFrame(y_pred, columns=output_features)

# === 6. Evaluation metrics ===
print("\nPer-element R² and MAE:")
for el in all_elements:
    r2 = r2_score(y_actual[el], y_pred_df[el])
    mae = mean_absolute_error(y_actual[el], y_pred_df[el])
    print(f"{el:>2}: R² = {r2:5.2f}, MAE = {mae:6.3f}")

# === 7. Plot actual vs predicted for key elements ===
important_elements = ["C", "N", "Si"]

# Set number of rows and columns for subplots
n = len(important_elements)
ncols = 2
nrows = (n + ncols - 1) // ncols  # Ensures enough rows

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6 * ncols, 5 * nrows))
axes = axes.flatten()  # Flatten in case of single row/column

for idx, el in enumerate(important_elements):
    actual = y_actual[el]
    predicted = y_pred_df[el]
    r2 = r2_score(actual, predicted)
    mae = mean_absolute_error(actual, predicted)

    ax = axes[idx]
    ax.scatter(actual, predicted, alpha=0.6, edgecolors='k')
    max_val = max(actual.max(), predicted.max())
    ax.plot([0, max_val], [0, max_val], 'r--', label='Ideal: y=x')

    ax.set_xlabel(f"Actual {el} Count")
    ax.set_ylabel(f"Predicted {el} Count")
    ax.set_title(f"{el} — Actual vs Predicted")
    ax.legend()
    ax.grid(True)

    metrics_text = f"R² = {r2:.3f}\nMAE = {mae:.3f}"
    ax.text(0.05, 0.95, metrics_text,
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Hide unused subplots, if any
for i in range(len(important_elements), len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()
plt.show()