import pandas as pd
import os
import logging
from collections import defaultdict

# === Setup Logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === CONFIG ===
input_csv_path = "data_generated/hive_density_staged.csv"
output_dir = "forecasting/output"
os.makedirs(output_dir, exist_ok=True)

continental_countries = [
    "France", "Spain", "Portugal", "Belgium", "Netherlands", "Germany", "Italy", "Switzerland",
    "Austria", "Luxembourg", "Czech Republic", "Slovakia", "Hungary", "Poland", "Slovenia",
    "Croatia", "Bosnia and Herzegovina", "Serbia", "Romania", "Bulgaria", "Greece", "Denmark",
    "Norway", "Sweden", "Finland", "Estonia", "Latvia", "Lithuania", "Ukraine"
]

neighbors = {
    "France": ["Belgium", "Spain", "Germany", "Italy", "Switzerland", "Luxembourg"],
    "Spain": ["Portugal", "France"],
    "Portugal": ["Spain"],
    "Belgium": ["France", "Netherlands", "Germany", "Luxembourg"],
    "Netherlands": ["Belgium", "Germany"],
    "Germany": ["Denmark", "Netherlands", "Belgium", "France", "Switzerland", "Austria", "Poland", "Czech Republic", "Luxembourg"],
    "Italy": ["France", "Switzerland", "Austria", "Slovenia"],
    "Switzerland": ["France", "Germany", "Italy", "Austria"],
    "Austria": ["Germany", "Czech Republic", "Slovakia", "Hungary", "Slovenia", "Switzerland", "Italy"],
    "Luxembourg": ["France", "Belgium", "Germany"],
    "Czech Republic": ["Germany", "Poland", "Slovakia", "Austria"],
    "Slovakia": ["Czech Republic", "Austria", "Hungary", "Poland", "Ukraine"],
    "Hungary": ["Slovakia", "Austria", "Slovenia", "Croatia", "Romania", "Ukraine"],
    "Poland": ["Germany", "Czech Republic", "Slovakia", "Ukraine", "Lithuania"],
    "Slovenia": ["Italy", "Austria", "Hungary", "Croatia"],
    "Croatia": ["Slovenia", "Hungary", "Bosnia and Herzegovina", "Serbia"],
    "Bosnia and Herzegovina": ["Croatia", "Serbia"],
    "Serbia": ["Bosnia and Herzegovina", "Croatia", "Hungary", "Romania", "Bulgaria"],
    "Romania": ["Hungary", "Serbia", "Ukraine", "Bulgaria"],
    "Bulgaria": ["Serbia", "Romania", "Greece"],
    "Greece": ["Bulgaria"],
    "Denmark": ["Germany"],
    "Norway": ["Sweden"],
    "Sweden": ["Norway", "Finland"],
    "Finland": ["Sweden", "Estonia"],
    "Estonia": ["Latvia", "Finland"],
    "Latvia": ["Estonia", "Lithuania"],
    "Lithuania": ["Latvia", "Poland"],
    "Ukraine": ["Poland", "Slovakia", "Hungary", "Romania"]
}

# === Load data ===
df = pd.read_csv(input_csv_path)
df = df[df["country"].isin(continental_countries)].copy()
df["year"] = df["year"].astype(int)
df["final_stage"] = df["final_stage"].astype(int)

if "hive_count" not in df.columns and "estimated_hives_without_weighting" in df.columns:
    df["hive_count"] = df["estimated_hives_without_weighting"]

df["stage_year"] = df.groupby(["country", "final_stage"])["year"].rank(method="dense").astype(int)

# === 1. Invasion order: when each country first reached stage 1 ===
logging.info("Identifying first invasion year per country...")
first_invasion = df[df["final_stage"] == 1].groupby("country")["year"].min().to_dict()
ordered_invasion = sorted(first_invasion.items(), key=lambda x: x[1])

# === 2. Identify spread triggers (when a neighbor became newly invaded) ===
logging.info("Mapping directional spread and capturing parent density at moment of neighbor invasion...")
spread_events = []

for country, year in ordered_invasion:
    if year is None:
        continue

    candidate_sources = []

    for potential_parent, parent_year in ordered_invasion:
        if potential_parent == country:
            continue
        if parent_year >= year:
            continue
        if country in neighbors.get(potential_parent, []):
            parent_status = df[(df["country"] == potential_parent) & (df["year"] == year - 1)]
            if not parent_status.empty:
                density = parent_status["hive_density"].values[0]
                hives = parent_status["hive_count"].values[0]
                candidate_sources.append({
                    "from": potential_parent,
                    "to": country,
                    "year": year,
                    "density_at_spread": density,
                    "hives_at_spread": hives
                })

    # Choose the best candidate: highest density
    if candidate_sources:
        best_source = max(candidate_sources, key=lambda x: x["density_at_spread"])
        spread_events.append(best_source)


spread_df = pd.DataFrame(spread_events)
spread_df.to_csv(f"{output_dir}/spread_thresholds_by_direction.csv", index=False)
logging.info("Saved directional spread thresholds.")

# === 3. Aggregate density and hive patterns by stage-year ===
logging.info("Calculating average density and hives per stage year across all countries...")
summary = df.groupby(["final_stage", "stage_year"]).agg(
    avg_density=("hive_density", "mean"),
    avg_hives=("hive_count", "mean"),
    num_countries=("country", "nunique")
).reset_index()

density_pivot = summary.pivot(index="stage_year", columns="final_stage", values="avg_density").round(5)
hives_pivot = summary.pivot(index="stage_year", columns="final_stage", values="avg_hives").round(1)

density_pivot.to_csv(f"{output_dir}/density_growth_by_stage_year.csv")
hives_pivot.to_csv(f"{output_dir}/hive_growth_by_stage_year.csv")

logging.info("Forecast foundation ready. Directional spread logic and growth by stage exported.")
