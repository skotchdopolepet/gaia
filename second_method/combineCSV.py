import csv

# --- Configuration ---
file1_name = "combined_main.csv"
file2_name = "combined_old format_to_2009.csv"
output_file_name = "merged_data.csv"
column_to_drop_from_file1 = "behavior"
# ---------------------

def combine_csvs(main_file, old_file, output_file, column_to_drop):
    """
    Combines two CSV files, dropping a specified column from the first file.
    The header of the second file is assumed to be the target header structure.
    """
    print(f"Combining '{main_file}' and '{old_file}' into '{output_file}'...")
    print(f"Dropping column '{column_to_drop}' from '{main_file}'.")

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            
            # --- Process the first file (combined_main.csv) ---
            try:
                with open(main_file, 'r', newline='', encoding='utf-8') as infile1:
                    reader1 = csv.reader(infile1)
                    
                    # Read and process header from the first file
                    header1 = next(reader1)
                    try:
                        drop_index = header1.index(column_to_drop)
                    except ValueError:
                        print(f"Error: Column '{column_to_drop}' not found in the header of '{main_file}'.")
                        print(f"Header found: {header1}")
                        return False

                    # Create the output header by excluding the dropped column
                    output_header = [col for i, col in enumerate(header1) if i != drop_index]
                    writer.writerow(output_header)
                    
                    # Process data rows from the first file
                    rows_written_file1 = 0
                    for row in reader1:
                        if len(row) == len(header1): # Ensure row has expected number of columns
                            modified_row = [cell for i, cell in enumerate(row) if i != drop_index]
                            writer.writerow(modified_row)
                            rows_written_file1 += 1
                        else:
                            print(f"Warning: Skipping malformed row in '{main_file}' (expected {len(header1)} columns, got {len(row)}): {row}")
                    print(f"Processed {rows_written_file1} data rows from '{main_file}'.")

            except FileNotFoundError:
                print(f"Error: File '{main_file}' not found.")
                return False
            except Exception as e:
                print(f"An error occurred while processing '{main_file}': {e}")
                return False

            # --- Process the second file (combined_old format_to_2009.csv) ---
            try:
                with open(old_file, 'r', newline='', encoding='utf-8') as infile2:
                    reader2 = csv.reader(infile2)
                    
                    # Skip header of the second file (assuming it matches output_header structure)
                    header2 = next(reader2)
                    if len(header2) != len(output_header):
                        print(f"Warning: Header of '{old_file}' has {len(header2)} columns, "
                              f"but expected {len(output_header)} based on '{main_file}' after dropping a column.")
                        print(f"Header of '{old_file}': {header2}")
                        print(f"Target header: {output_header}")
                        # Continue, but be aware of potential mismatches.

                    # Process data rows from the second file
                    rows_written_file2 = 0
                    for row in reader2:
                        if len(row) == len(output_header): # Check against the target number of columns
                            writer.writerow(row)
                            rows_written_file2 += 1
                        elif len(row) == len(header2): # If it matches its own header but not target
                            print(f"Warning: Row in '{old_file}' matches its own header columns ({len(header2)}) "
                                  f"but not target columns ({len(output_header)}). Skipping: {row}")
                        else:
                             print(f"Warning: Skipping malformed row in '{old_file}' (expected {len(header2)} or {len(output_header)} columns, got {len(row)}): {row}")
                    print(f"Processed {rows_written_file2} data rows from '{old_file}'.")

            except FileNotFoundError:
                print(f"Error: File '{old_file}' not found.")
                return False # Or decide if partial completion is okay
            except Exception as e:
                print(f"An error occurred while processing '{old_file}': {e}")
                return False

        print(f"Successfully combined files into '{output_file}'.")
        return True

    except IOError:
        print(f"Error: Could not write to output file '{output_file}'. Check permissions.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":

    
    # Combine the CSVs
    success = combine_csvs(file1_name, file2_name, output_file_name, column_to_drop_from_file1)

    if success:
        print("\n--- Contents of the merged file: ---")
        try:
            with open(output_file_name, 'r', newline='', encoding='utf-8') as f:
                for line in f:
                    print(line, end='')
        except FileNotFoundError:
            print(f"Could not read '{output_file_name}' to display contents.")