import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# -----------------------
# Load Dataset
# -----------------------
df = pd.read_csv("ml/data/repository_dataset.csv")

# -----------------------
# Normalize numeric columns
# -----------------------
columns = [
    "stars",
    "forks",
    "watchers",
    "readme_score",
    "dependency_count",
    "tech_stack_count",
    "language_count"
]

scaler = MinMaxScaler()

df[columns] = scaler.fit_transform(df[columns])

# -----------------------
# Binary features
# -----------------------
df["has_license"] = df["has_license"].astype(int)
df["has_gitignore"] = df["has_gitignore"].astype(int)
df["has_readme"] = df["has_readme"].astype(int)

# -----------------------
# Health Score Formula
# -----------------------
df["health_score"] = (

      0.30 * df["stars"]
    + 0.15 * df["forks"]
    + 0.10 * df["watchers"]
    + 0.15 * df["readme_score"]
    + 0.10 * df["dependency_count"]
    + 0.05 * df["language_count"]
    + 0.05 * df["tech_stack_count"]
    + 0.05 * df["has_readme"]
    + 0.03 * df["has_license"]
    + 0.02 * df["has_gitignore"]

) * 100

# -----------------------
# Save
# -----------------------
df.to_csv(
    "ml/data/repository_dataset_scored.csv",
    index=False
)

print(df[["repository", "health_score"]].head())

print("\nDataset saved successfully!")