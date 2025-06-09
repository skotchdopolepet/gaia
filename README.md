# Asian Hornet (Vespa velutina) Spread and Impact Model - GAIA

A predictive model for forecasting the spread of the invasive Asian Hornet in Europe and its potential impact on honeybee populations.

## About The Project

This project was developed by the **GAIA Data Club Team** to model the threat posed by the invasive Asian Hornet (*Vespa velutina*) to European biodiversity and honeybees.

Leveraging observational data primarily from **GAIA.eco** alongside public and scientific sources, this repository contains the code to:
1.  Analyze the historical progression of the invasion (2004-2025).
2.  Forecast future spread based on ecological patterns through 2050.
3.  Simulate the potential impact on honeybee colonies under different scenarios.

## The Team

This model was created by a team of Applied Data Analytics & AI Master's Students at the University of Economics in Prague, as our Data Project .

- Barbora Zelníková
- Oleksandra Tiurina
- Adriana Slúková
- Mária Kuczik
- Vlastimil Peer

## Core Methodology

The model is built on a country-level, **stage-based density** approach. Each country's invasion status is classified into one of three stages based on its calculated hornet hive density (`hives per km²`):

*   **Stage 1: Newly Invaded** - Initial establishment phase with low density.
*   **Stage 2: Expanding Rapidly** - Accelerated growth and population establishment.
*   **Stage 3: Saturated** - The population nears the environment's carrying capacity.

Growth rates and cross-border spread are determined by a country's current stage, simulating a realistic invasion lifecycle.

## Workflow

The codebase follows a clear, sequential workflow:

1.  **Data Preparation:** Gathers and cleans hornet occurrence data, filtering for the active season (March-November) to ensure accuracy.
2.  **Historical Analysis (2004-2025):** Estimates historical hive counts by clustering sightings within a 2km radius and calibrates these estimates against known nest data.
3.  **Hornet Spread Forecast (2026-2050):** Projects future hive density using stage-specific growth formulas and a cross-border spread mechanism.
4.  **Bee Population Impact:** Simulates potential honeybee decline based on projected hornet density, using **Optimistic**, **Realistic**, and **Pessimistic** scenarios.
5.  **Visualization:** Combines historical and forecasted data to generate maps and charts illustrating the spread over time.

## Key Outputs

Running the scripts in this repository will generate:

*   `hive_density_staged.csv`: Calibrated historical data with hive counts and invasion stages per country (2004-2025).
*   `forecast_2026_to_2050.csv`: The core forecast data detailing predicted stage, hive density, and total hive counts.
*   **Visualizations** (e.g., `combined_visual.png`): Maps and charts providing an intuitive understanding of the hornet's spread.

---

### Dive Deeper

For a comprehensive breakdown of the methodology, data sources, formula derivations, and validation processes, please review our team's complete project documentation.

➡️ **[View the Full Project Documentation](https://www.notion.so/GAIA-doc-1fe731aa8a80801dbcfdd3332cc4193f)**

We also created a more business-oriented website to present the project's findings and implications.

➡️ **[Visit the Project Website](https://ludicrous-scilla-f14.notion.site/MIGRATION-OF-ASIAN-HORNET-1fc214fe9d84800b9943f4afdb2a74b3)**

This work was conducted in partnership with GAIA. To learn more about their mission to provide global biodiversity data, visit their website.

➡️ **[Visit GAIA](https://illuminum.se/)**
