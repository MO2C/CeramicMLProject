import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.read_csv("heating_operations_only.csv")

# Select only numeric columns (excluding identifiers)
numeric_cols = df.select_dtypes(include='number')

# Compute correlation matrix
corr_matrix = numeric_cols.corr()

# Plot heatmap
plt.figure(figsize=(16, 14))
sns.heatmap(corr_matrix, cmap='coolwarm', annot=False, fmt=".2f", square=True)
plt.title("Correlation Heatmap of Numeric Features", fontsize=16)
plt.tight_layout()
plt.show()