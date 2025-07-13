import pandas as pd
import joblib
import numpy as np

# === 1. Load the trained model ===
model = joblib.load("tuned_composition_predictor.pkl")  # Ensure this file exists in the working directory

# === 2. Define the input feature space ===
element_cols = ["O", "N", "C", "B", "Si", "Al", "Mg", "Zr", "Ti", "Ca", "Y", "Hf", "Fe", "Na",
                "K","Ba", "Sr", "Li", "Be", "Mn", "V", "Cr", "Nb", "Mo", "W", "Re",
                "Sc", "La", "Ce", "Th", "U"]
input_features = element_cols + ["Tm"]

# === 3. Define all output elements (must match model training output order) ===
# Manually listed here or load from training context
all_elements = sorted(list(set(element_cols)))  # If you used formula parsing during training, load this list instead

# === 4. Create a sample input ===
# Example: 1 unit of Nb and P, melting temperature = 2000 K
input_example = {el: 1 if el in ["N", "Ti","O"] else 0 for el in element_cols}
input_example["Tm"] = 1400.75  # Replace with actual input

input_df = pd.DataFrame([input_example])

# === 5. Predict ===
prediction = model.predict(input_df)[0]

# === 6. Convert to readable format ===
predicted_composition = {
    el: round(prediction[i], 2)
    for i, el in enumerate(all_elements)
    if prediction[i] > 0.05  # Optional: Filter low-contribution elements
}

scale_factor = 100
scaled_composition = {el: round(val * scale_factor) for el, val in predicted_composition.items()}

# === 7. Output ===
print("Predicted composition:")
for el, val in scaled_composition.items():
    print(f"{el}: {val}")