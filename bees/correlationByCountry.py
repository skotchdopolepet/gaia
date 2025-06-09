#!/usr/bin/env python3
"""
File: outputs/correlate_hornet_bee.py
Description: Calculates per-country correlation between hornet metrics and bee density growth.
Outputs correlation for both hive density and hive count vs. bee growth.
"""

import os
import pandas as pd
from scipy.stats import pearsonr

# === PATHS ===
hornet_path = "output/hornet_combined_corrected.csv"
bee_path = "output/bee_density_trends.csv"
output_path = "output/correlationByCountry.csv"
os.makedirs("output", exist_ok=True)

# === LOAD DATA ===
hornets = pd.read_csv(hornet_path)
bees = pd.read_csv(bee_path)

# === CLEAN & PREP ===
hornets = hornets.rename(columns={
    "hive_density": "Hornet_Density",
    "hive_count": "Hornet_Count",
    "stage": "Invasion_Stage"
})
bees = bees.rename(columns={"Bee_Density_Growth": "Bee_Growth"})

hornets["Country"] = hornets["Country"].str.strip()
bees["Country"] = bees["Country"].str.strip()

# === MERGE FOR CORRELATION ===
merged = pd.merge(
    hornets[["Country", "Year", "Hornet_Density", "Hornet_Count"]],
    bees[["Country", "Year", "Bee_Growth"]],
    on=["Country", "Year"],
    how="inner"
)

# === PER-COUNTRY CORRELATIONS ===
results = []
for country in merged["Country"].unique():
    sub = merged[merged["Country"] == country].dropna()
    if len(sub) >= 5:
        # Correlation: Hornet_Density vs Bee_Growth
        r_density, p_density = pearsonr(sub["Hornet_Density"], sub["Bee_Growth"])
        # Correlation: Hornet_Count vs Bee_Growth
        r_count, p_count = pearsonr(sub["Hornet_Count"], sub["Bee_Growth"])

        results.append({
            "Country": country,
            "Density_vs_BeeGrowth_r": round(r_density, 4),
            "Density_p_value": round(p_density, 4),
            "Count_vs_BeeGrowth_r": round(r_count, 4),
            "Count_p_value": round(p_count, 4),
            "Data_Points": len(sub)
        })

# === OUTPUT ===
cor_df = pd.DataFrame(results).sort_values("Density_vs_BeeGrowth_r")
cor_df.to_csv(output_path, index=False)
print(f"✅ Correlation results saved to: {output_path}")
