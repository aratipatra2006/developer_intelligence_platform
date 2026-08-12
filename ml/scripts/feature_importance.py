import pandas as pd
import joblib

# Load trained pipeline
model = joblib.load(
    "ml/models/repository_health_model.pkl"
)

# Get preprocessing and Random Forest
preprocessor = model.named_steps["preprocessor"]
rf_model = model.named_steps["model"]

# Get transformed feature names
feature_names = preprocessor.get_feature_names_out()

# Get importance values
importances = rf_model.feature_importances_

# Create table
importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
})

# Sort
importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

print("\n")
print("FEATURE IMPORTANCE")

print(
    importance_df.head(20).to_string(index=False)
)

# Save results
importance_df.to_csv(
    "ml/data/feature_importance.csv",
    index=False
)

print("\nFeature importance saved to:")
print("ml/data/feature_importance.csv")