import pandas as pd

# Read metadata
df = pd.read_csv("ml/dataset/repositories_metadata.csv")

print("Repositories before filtering:", len(df))

# Apply filters
filtered = df[
    (df["size"] < 20000) &          # Less than ~20 MB
    (df["archived"] == False) &
    (df["fork"] == False) &
    (df["language"].notna())
]

print("Repositories after filtering:", len(filtered))

# Save filtered metadata
filtered.to_csv(
    "ml/dataset/repositories_filtered.csv",
    index=False
)

# Save only URLs for build_dataset.py
filtered["url"].to_csv(
    "ml/dataset/repositories.txt",
    index=False,
    header=False
)

print("Filtering completed successfully!")