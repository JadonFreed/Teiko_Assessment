import pandas as pd

def calculate_relative_frequencies(csv_path):
    # Load the data
    df = pd.read_csv(csv_path)
    
    # Define the columns that contain cell counts
    cell_cols = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    
    # Create a working copy with just the sample ID and cell counts
    df_counts = df[['sample'] + cell_cols].copy()
    
    # 1. Calculate the total_count for each sample by summing across the cell columns
    df_counts['total_count'] = df_counts[cell_cols].sum(axis=1)
    
    # 2. Reshape (melt) the dataframe from wide to long format
    df_long = pd.melt(
        df_counts, 
        id_vars=['sample', 'total_count'], 
        value_vars=cell_cols, 
        var_name='population', 
        value_name='count'
    )
    
    # 3. Calculate relative frequency in percentage
    df_long['percentage'] = (df_long['count'] / df_long['total_count']) * 100
    
    # 4. Reorder the columns to match Bob's requirements exactly
    df_long = df_long[['sample', 'total_count', 'population', 'count', 'percentage']]
    
    # Sort by sample and population for better readability
    df_long = df_long.sort_values(by=['sample', 'population']).reset_index(drop=True)
    
    return df_long

if __name__ == "__main__":
    # Execute the function
    summary_table = calculate_relative_frequencies('cell-count.csv')
    
    # Display the first few rows to verify
    print(summary_table.head(10))
    
    # Save the output to a CSV file for future use (like in the dashboard)
    output_file = 'part2_summary.csv'
    summary_table.to_csv(output_file, index=False)
    print(f"\nSummary table successfully saved to {output_file}")