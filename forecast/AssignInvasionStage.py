#!/usr/bin/env python3
"""
File: forecasting/AssignInvasionStage.py
Description: Classify each country-year by invasion stage based on hive density.
            Enforces monotonic progression — once a country reaches a higher stage,
            it cannot revert to a lower one in later years.
Output: forecasting/data_generated/hive_density_staged.csv
"""

import os
import logging
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Input and output paths
input_csv_path = "data_generated/hive_density_by_country_year.csv"
output_csv_path = "data_generated/hive_density_staged.csv"

def classify_stage(density):
    """
    Assign invasion stage based on density (updated thresholds).
    """
    if pd.isna(density):
        return None
    elif density < 0.0002:
        return 1  # Newly Invaded
    elif density < 0.005:
        return 2  # Expanding
    else:
        return 3  # Saturated

def enforce_stage_progression(df):
    """
    For each country, ensure that invasion stages do not regress over time.
    A country can only remain the same or move to a higher stage.
    """
    df = df.sort_values(by=["country", "year"]).copy()
    df["final_stage"] = None

    max_stage_so_far = {}

    for idx, row in df.iterrows():
        country = row["country"]
        current_stage = row["invasion_stage"]

        if pd.isna(current_stage):
            df.at[idx, "final_stage"] = None
            continue

        previous_max = max_stage_so_far.get(country, 1)
        locked_stage = max(previous_max, current_stage)

        df.at[idx, "final_stage"] = locked_stage
        max_stage_so_far[country] = locked_stage

    return df

def main():
    try:
        df = pd.read_csv(input_csv_path)
        logger.info(f"Loaded hive density data with {len(df)} rows.")

        # Step 1: Assign stage from density
        df["invasion_stage"] = df["hive_density"].apply(classify_stage)

        # Step 2: Apply no-regression rule
        staged_df = enforce_stage_progression(df)

        # Optional: add readable labels
        stage_labels = {1: "Newly Invaded", 2: "Expanding", 3: "Saturated"}
        staged_df["stage_label"] = staged_df["final_stage"].map(stage_labels)

        # Save output
        staged_df.to_csv(output_csv_path, index=False)
        logger.info(f"Staged invasion data saved to {output_csv_path}")

    except Exception as e:
        logger.error(f"Error while assigning invasion stages: {e}")
        raise

if __name__ == "__main__":
    main()
