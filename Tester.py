import pandas as pd
import numpy as np
import joblib
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score, mean_absolute_error

# === 1. Load the trained model ===
model = joblib.load("composition_predictor.pkl")  # Ensure this .pkl file is in the same folder

# === 2. Load the dataset ===
df = pd.read_csv("test_data.csv")

# === 3. Define input features (must match model training) ===
element_cols = ["O", "N", "C", "B", "Si", "Al", "Mg", "Zr", "Ti", "Ca", "Y", "Hf", "Fe", "Na",
                "K","Ba", "Sr", "Li", "Be", "Mn", "V", "Cr", "Nb", "Mo", "W", "Re",
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

# Use seaborn style for clean visuals
sns.set(style="whitegrid")

important_elements = ["C", "O", "N", "B"]

plt.figure(figsize=(10, 8))

r2_list = []
mae_list = []

colors = sns.color_palette("Set2", len(important_elements))

for i, el in enumerate(important_elements):
    actual = y_actual[el]
    predicted = y_pred_df[el]

    r2 = r2_score(actual, predicted)
    mae = mean_absolute_error(actual, predicted)
    r2_list.append(r2)
    mae_list.append(mae)

    # No edgecolors, solid color dots
    plt.scatter(actual, predicted, 
                label=f"{el} (R²={r2:.2f}, MAE={mae:.3f})", 
                alpha=0.8, s=60, color=colors[i])

# Solid thin y = x line
combined_actual = pd.concat([y_actual[el] for el in important_elements])
combined_pred = pd.concat([y_pred_df[el] for el in important_elements])
max_val = max(combined_actual.max(), combined_pred.max())
plt.plot([0, max_val], [0, max_val], color='gray', linewidth=1.2, label='Ideal: y = x')

# Average metrics annotation
avg_r2 = sum(r2_list) / len(r2_list)
avg_mae = sum(mae_list) / len(mae_list)

plt.text(0.05, 0.95, f"Average R² = {avg_r2:.3f}\nAverage MAE = {avg_mae:.3f}",
         transform=plt.gca().transAxes,
         verticalalignment='top',
         fontsize=12,
         bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85))

# Styling
plt.xlabel("Actual Element Count", fontsize=11)
plt.ylabel("Predicted Element Count", fontsize=11)
plt.title("Actual vs. Predicted Elemental Counts", fontsize=15)
# plt.legend(title="Elements", fontsize=10, loc='upper left')
plt.grid(False)
plt.tight_layout()
plt.show()