import pandas as pd

# --- Configuration ---
INPUT_CSV = "potential_nests_with_counts.csv"
OUTPUT_CSV = "yearly_country_nest_summary.csv"

def generate_yearly_country_summary():
    print(f"Loading data from {INPUT_CSV}...")
    try:
        nests_df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_CSV}' not found.")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    if nests_df.empty:
        print(f"The input file '{INPUT_CSV}' is empty. No summary to generate.")
        return

    print(f"Generating yearly summary of nests per country...")

    # Group by 'year' and 'country', then count the number of nests in each group
    # .size() creates a Series with MultiIndex (year, country) and values as counts
    # .reset_index(name='amount_of_nests') converts this Series to a DataFrame
    # and names the count column appropriately.
    summary_df = nests_df.groupby(['year', 'country']).size().reset_index(name='amount_of_nests')

    # Sort the results for better readability (optional)
    summary_df = summary_df.sort_values(by=['year', 'country'])

    print(f"\nSummary generated with {len(summary_df)} rows.")
    print(f"Saving summary to {OUTPUT_CSV}...")
    try:
        summary_df.to_csv(OUTPUT_CSV, index=False)
        print("Done.")
        print(f"\nFirst few lines of the summary ({OUTPUT_CSV}):")
        print(summary_df.head())
    except Exception as e:
        print(f"Error saving output CSV: {e}")

if __name__ == "__main__":
    generate_yearly_country_summary()