import os
import pandas as pd
import glob
from pathlib import Path

def find_and_combine_csvs(directory="GAIA"):
    """
    Find all CSV files in the specified directory and combine them into a single DataFrame
    based on matching column formats.
    
    Args:
        directory (str): The directory to search for CSV files
        
    Returns:
        DataFrame: Combined DataFrame of all CSV files with matching formats
        dict: Dictionary of DataFrames that couldn't be combined (grouped by column format)
    """
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return None, None
    
    # Find all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory, "**", "*.csv"), recursive=True)
    
    if not csv_files:
        print(f"No CSV files found in '{directory}'.")
        return None, None
    
    print(f"Found {len(csv_files)} CSV files.")
    
    # Dictionary to store DataFrames grouped by their column signature
    format_groups = {}
    
    # Process each CSV file
    for file_path in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Create a signature based on column names
            column_signature = tuple(df.columns)
            
            # Group DataFrames by column signature
            if column_signature not in format_groups:
                format_groups[column_signature] = []
            
            format_groups[column_signature].append((file_path, df))
            print(f"Processed: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Combine DataFrames with the same column format
    combined_dfs = {}
    for column_signature, file_df_pairs in format_groups.items():
        if len(file_df_pairs) > 1:
            # Extract just the DataFrames
            dfs = [df for _, df in file_df_pairs]
            
            # Combine all DataFrames with the same columns
            combined_df = pd.concat(dfs, ignore_index=True)
            combined_dfs[column_signature] = combined_df
            
            file_names = [Path(file_path).name for file_path, _ in file_df_pairs]
            print(f"Combined {len(dfs)} files with columns {column_signature}:")
            print(f"  - Files: {', '.join(file_names)}")
        else:
            # If there's only one file with this format, just add it as is
            file_path, df = file_df_pairs[0]
            combined_dfs[column_signature] = df
            print(f"Unique column format found in {Path(file_path).name}: {column_signature}")
    
    # Find the most common format (the one with the most files combined)
    if combined_dfs:
        main_format = max(format_groups.keys(), key=lambda k: len(format_groups[k]))
        main_combined_df = combined_dfs[main_format]
        remaining_dfs = {k: v for k, v in combined_dfs.items() if k != main_format}
        
        return main_combined_df, remaining_dfs
    
    return None, None

def save_combined_data(main_df, other_dfs, output_dir="GAIA_combined"):
    """
    Save the combined DataFrames to CSV files.
    
    Args:
        main_df (DataFrame): The main combined DataFrame
        other_dfs (dict): Dictionary of other DataFrames that couldn't be combined with the main one
        output_dir (str): Directory to save the output files
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the main combined DataFrame
    if main_df is not None:
        main_output_path = os.path.join(output_dir, "combined_main.csv")
        main_df.to_csv(main_output_path, index=False)
        print(f"Main combined data saved to: {main_output_path}")
    
    # Save the other DataFrames
    for i, (cols, df) in enumerate(other_dfs.items() if other_dfs else {}.items()):
        format_name = f"format_{i+1}"
        output_path = os.path.join(output_dir, f"combined_{format_name}.csv")
        df.to_csv(output_path, index=False)
        print(f"Additional format data saved to: {output_path}")

if __name__ == "__main__":
    # Find and combine CSV files
    main_df, other_dfs = find_and_combine_csvs("GAIA")
    
    if main_df is not None:
        print("\nMain combined DataFrame:")
        print(f"- Shape: {main_df.shape}")
        print(f"- Columns: {list(main_df.columns)}")
        
        # Save the combined data
        save_combined_data(main_df, other_dfs)
    else:
        print("No CSV files could be combined.")