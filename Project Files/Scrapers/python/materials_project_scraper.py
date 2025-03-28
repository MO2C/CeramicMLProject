from mp_api.client import MPRester
import pandas as pd

# Set your Materials Project API key
API_KEY = "your_api_key_here"

# List of common ceramic elements
CERAMIC_ELEMENTS = [
    "O", "N", "C", "B", "Si", "Al", "Mg", "Zr", "Ti", "Ca", "Y", "Hf",
    "Fe", "Na", "K", "P", "S", "Ba", "Sr", "Li", "Be", "Mn", "V", "Cr",
    "Nb", "Mo", "W", "Re", "Sc", "La", "Ce", "Th", "U"
]

# Initialize API client
with MPRester(API_KEY) as mpr:
    # Query for ceramic-like materials (non-metals, band gap > 0)
    materials = mpr.materials.search(
        elements=CERAMIC_ELEMENTS,
        band_gap=(0.1, None),  # Exclude metals
        fields=[
            "material_id", "formula_pretty", "band_gap", "efermi",
            "formation_energy_per_atom", "energy_above_hull", "decomposes",
            "elasticity", "bulk_modulus", "shear_modulus",
            "density", "crystal_system", "spacegroup", "cif"
        ]
    )

# Convert results to DataFrame
df = pd.DataFrame(materials)

# Save to CSV
df.to_csv("ceramic_materials.csv", index=False)

print(f"Downloaded {len(df)} ceramic materials and saved to ceramic_materials.csv")
