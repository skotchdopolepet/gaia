import pandas as pd
import os
 
# === ⬇️ Load tvoje forecast dáta ===
forecast_path = "/content/forecast_2026_to_2050 (1).csv"
df_forecast = pd.read_csv(forecast_path)
 
# === ⬇️ Load predation_score (2024) ===
predation_path = "output/predation_score_2024_scaled.csv"
df_predation = pd.read_csv(predation_path)[["country", "predation_score"]]
 
# === 🔗 Spojenie podľa krajiny ===
df_combined = df_forecast.merge(df_predation, on="country", how="left")
df_combined["predation_score"].fillna(0.0, inplace=True)  # pre istotu
 
# === 🧮 Adjust hive_density podľa predátorov ===
df_combined["adjusted_hive_density"] = df_combined["hive_density"].astype(float) * (1 - df_combined["predation_score"])
 
# === 💾 Export výstupu ===
os.makedirs("output", exist_ok=True)
output_path = "output/forecast_with_predation_adjustment.csv"
df_combined.to_csv(output_path, index=False)
 
print(f"✅ Upravený forecast uložený do: {output_path}")