#!/usr/bin/env python3
"""
File: forecasting/ComputeHiveDensity.py
Description: Compute hive density (hives/km²) for each country per year.
Output: forecasting/data_generated/hive_density_by_country_year.csv
"""

import os
import logging
import pandas as pd
import geopandas as gpd

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define relative paths
hive_csv_path = "../preparingHistoricalData/estimated_hives_weighted_output_clamped.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_csv_path = "data_generated/hive_density_by_country_year.csv"

# Ensure output directory exists
os.makedirs("data_generated", exist_ok=True)


def load_hive_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded hive data from {csv_path} with {len(df)} records.")
        return df
    except Exception as e:
        logger.error(f"Error loading hive data: {e}")
        raise


def aggregate_weighted_hive_counts(df):
    """
    Count estimated hives per country and year (each row = one weighted hive).
    """
    if not {'country', 'year'}.issubset(df.columns):
        raise ValueError("Input CSV must include 'country' and 'year' columns.")

    agg_df = df[['country', 'year', 'estimated_hives_with_weighting']].copy()
    agg_df.rename(columns={'estimated_hives_with_weighting': 'hive_count'}, inplace=True)
    logger.info("Aggregated hive counts by year and country.")
    return agg_df


def load_country_boundaries(shapefile_path):
    try:
        gdf = gpd.read_file(shapefile_path)
        logger.info(f"Loaded country shapefile from {shapefile_path} with {len(gdf)} records.")
        gdf = gdf.to_crs(epsg=6933)  # Equal-area projection
        gdf['area_km2'] = gdf['geometry'].area / 1e6
        logger.info("Computed area in km² after reprojection.")
        return gdf[['ADMIN', 'area_km2']]
    except Exception as e:
        logger.error(f"Error loading country boundaries: {e}")
        raise


def merge_hive_data_and_areas(hive_df, country_gdf):
    merged_df = pd.merge(hive_df, country_gdf, left_on='country', right_on='ADMIN', how='left')
    missing = merged_df['area_km2'].isnull().sum()
    if missing > 0:
        logger.warning(f"{missing} records have missing area values after merging.")
    else:
        logger.info("All hive records successfully matched with area data.")
    return merged_df


def compute_hive_density(merged_df):
    merged_df['hive_density'] = merged_df['hive_count'] / merged_df['area_km2']
    logger.info("Hive density computation complete.")
    return merged_df


def main():
    hive_df = load_hive_data(hive_csv_path)
    hive_counts_df = aggregate_weighted_hive_counts(hive_df)
    country_gdf = load_country_boundaries(shapefile_path)
    merged_df = merge_hive_data_and_areas(hive_counts_df, country_gdf)
    density_df = compute_hive_density(merged_df)
    density_df.to_csv(output_csv_path, index=False)
    logger.info(f"Hive density data saved to {output_csv_path}")


if __name__ == "__main__":
    main()
