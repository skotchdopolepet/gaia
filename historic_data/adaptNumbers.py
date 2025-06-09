#!/usr/bin/env python3
"""
File: preparingHistoricalData/adaptNumbers.py
Description:
1. Inject assumed nest counts for Portugal and Spain.
2. Add official historical counts from Vlasta where missing.
3. Fill gaps in time series for countries with re-appearances using average estimation.
Output: Updates estimated_hives_weighted_output_clamped.csv
"""

import os
import pandas as pd

# Paths
input_csv = "estimated_hives_weighted_output_clamped.csv"
output_csv = "estimated_hives_weighted_output_clamped.csv"
vlasta_csv = "vlasta/yearly_country_nest_summary.csv"

# Load original table
df = pd.read_csv(input_csv)

# -------------------------
# 1. Manual Portugal & Spain injection
manual_entries = [
    # Portugal (2011–2020)
    {"year": 2011, "country": "Portugal", "count": 1},
    {"year": 2012, "country": "Portugal", "count": 3},
    {"year": 2013, "country": "Portugal", "count": 9},
    {"year": 2014, "country": "Portugal", "count": 27},
    {"year": 2015, "country": "Portugal", "count": 81},
    {"year": 2016, "country": "Portugal", "count": 243},
    {"year": 2017, "country": "Portugal", "count": 486},
    {"year": 2018, "country": "Portugal", "count": 648},
    {"year": 2019, "country": "Portugal", "count": 732},
    {"year": 2020, "country": "Portugal", "count": 817},
    # Spain (2010–2011)
    {"year": 2010, "country": "Spain", "count": 10},
]

manual_df = pd.DataFrame([
    {
        "year": entry["year"],
        "country": entry["country"],
        "estimated_hives_without_weighting": entry["count"],
        "final_weight": 1.0,
        "estimated_hives_with_weighting": entry["count"],
        "official_nest_count": entry["count"]
    }
    for entry in manual_entries
])

df = df[~df.set_index(["year", "country"]).index.isin(manual_df.set_index(["year", "country"]).index)]
df = pd.concat([df, manual_df], ignore_index=True)

# -------------------------
# 2. Inject missing historical records from Vlasta
vlasta_df = pd.read_csv(vlasta_csv).rename(columns={"amount_of_nests": "count"})

existing_index = df.set_index(["year", "country"]).index
missing_vlasta = vlasta_df[~vlasta_df.set_index(["year", "country"]).index.isin(existing_index)]

vlasta_entries = pd.DataFrame([
    {
        "year": row["year"],
        "country": row["country"],
        "estimated_hives_without_weighting": row["count"],
        "final_weight": pd.NA,
        "estimated_hives_with_weighting": row["count"],
        "official_nest_count": pd.NA
    }
    for _, row in missing_vlasta.iterrows()
])

df = pd.concat([df, vlasta_entries], ignore_index=True)

# -------------------------
# 3. Fill year gaps with average estimations
df = df.sort_values(by=["country", "year"])
filled_rows = []

for country, group in df.groupby("country"):
    group_sorted = group.sort_values("year")
    years = group_sorted["year"].tolist()

    for i in range(len(years) - 1):
        y1 = years[i]
        y2 = years[i + 1]

        if y2 - y1 > 1:
            val1 = group_sorted[group_sorted["year"] == y1]["estimated_hives_with_weighting"].values[0]
            val2 = group_sorted[group_sorted["year"] == y2]["estimated_hives_with_weighting"].values[0]

            if pd.notna(val1) and pd.notna(val2):
                for missing_year in range(y1 + 1, y2):
                    avg_val = (val1 + val2) / 2
                    filled_rows.append({
                        "year": missing_year,
                        "country": country,
                        "estimated_hives_without_weighting": avg_val,
                        "final_weight": pd.NA,
                        "estimated_hives_with_weighting": avg_val,
                        "official_nest_count": pd.NA
                    })

# Append filled rows
if filled_rows:
    df = pd.concat([df, pd.DataFrame(filled_rows)], ignore_index=True)

# -------------------------
# Final sorting and saving
df = df.sort_values(by=["country", "year"])
df.to_csv(output_csv, index=False)
print(f"✅ Updated file saved to: {output_csv}")
