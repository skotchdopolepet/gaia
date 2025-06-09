#!/usr/bin/env python3
"""
File: forecasting/VisualizeInvasionStages.py
Description: Visualize invasion stage progression with visible vertical spacing.
Output: forecasting/plots/invasion_stage_over_time_spaced.png
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# Paths
input_csv_path = "forecasting/output/forecast_2026_to_2050.csv"
output_folder = "forecasting/plots"
os.makedirs(output_folder, exist_ok=True)
output_image_path = os.path.join(output_folder, "invasion_stage_over_time_spaced.png")

# Load and prepare data
df = pd.read_csv(input_csv_path)
df = df.dropna(subset=["stage"])
df["year"] = df["year"].astype(int)
df["stage"] = df["stage"].astype(int)

# Color for stages
stage_colors = {1: "#99d98c", 2: "#f9c74f", 3: "#f94144"}

# Set up plot
countries = sorted(df["country"].unique())
fig, ax = plt.subplots(figsize=(14, 0.4 * len(countries) + 2))

# Plot each country as a vertically offset line
for i, country in enumerate(countries):
    sub = df[df["country"] == country].sort_values("year")
    offset_y = i * 4
    y_vals = sub["stage"] + offset_y

    ax.plot(sub["year"], y_vals, color="#333333", linewidth=1.5, zorder=2)
    ax.scatter(sub["year"], y_vals, c=[stage_colors[s] for s in sub["stage"]],
               edgecolors="black", s=60, zorder=3)

    ax.text(sub["year"].min() - 1, offset_y + 2, country, va='center', ha='right', fontsize=9)

# Clean up axis
ax.set_yticks([])
ax.set_xlabel("Year", fontsize=12)
ax.set_title("Forecasted Invasion Stage Progression by Country (Spaced View)", fontsize=14)
ax.grid(axis='x', linestyle="--", alpha=0.4)
plt.tight_layout()

# Save
plt.savefig(output_image_path, dpi=300)
print(f"✅ Saved plot to: {output_image_path}")
