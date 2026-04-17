import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

def analyze_part3():
    df_meta = pd.read_csv('cell-count.csv')[
        ['sample', 'condition', 'treatment', 'sample_type', 'response']
    ].drop_duplicates()
    
    # load relative frequencies from Part 2
    df_summary = pd.read_csv('part2_summary.csv')
    
    # merge data with frequencies
    df_merged = pd.merge(df_summary, df_meta, on='sample', how='inner')
    
    # filter criteria: melanoma, miraclib, sample is PBMC
    df_filtered = df_merged[
        (df_merged['condition'] == 'melanoma') &
        (df_merged['treatment'] == 'miraclib') &
        (df_merged['sample_type'] == 'PBMC')
    ].copy()
    
    # drop rows without a valid response label
    df_filtered = df_filtered.dropna(subset=['response'])
    
    # create boxplot comparing responders vs non-responders for each cell population
    plt.figure(figsize=(10, 6))
    
   # order by population (cell type) 
    order = sorted(df_filtered['population'].unique())
    
    sns.boxplot(
        data=df_filtered, 
        x='population', 
        y='percentage', 
        hue='response',
        order=order
    )
    
    plt.title('Relative Frequencies of Immune Cells in Melanoma PBMC (Miraclib)\nResponders vs Non-Responders')
    plt.ylabel('Relative Frequency (%)')
    plt.xlabel('Cell Population')
    
    plt.tight_layout()
    plot_filename = 'part3_boxplot.png'
    plt.savefig(plot_filename)
    print(f"Boxplot saved successfully to {plot_filename}")
    
    # Statistical Analysis
    ## this section is motivated from a simple analysis on the distribution of the data and the variances between responders and non-responders.
    ## reference the analysis in part3_analysis.py for more details.
    results = []
    populations = df_filtered['population'].unique()
    
    for i, pop in enumerate(populations):
        pop_subset = df_filtered[df_filtered['population'] == pop]
        res_y = pop_subset[pop_subset['response'] == 'yes']['percentage']
        res_n = pop_subset[pop_subset['response'] == 'no']['percentage']

        # Welch's T-test  (parametric)
        ## given that sample sizes for each group are similar (around 950), all cell types show unequal variances between resp and non-resp (except for cd4_t_cell)
        ## we will use Welch's t test to account for unequal variances. 
        _, p_welch = stats.ttest_ind(res_y, res_n, equal_var=False)
        
        # Mann-Whitney U Test (Non-parametric)
        ## gives robust estimate by ranking, which should account for possible outliers and non-normality in the data.
        _, p_mw = stats.mannwhitneyu(res_y, res_n)

        

        print(f"{pop:12} | MW-U p: {p_mw:.4f} | Welch p: {p_welch:.4f}")
        
        results.append({
            'population': pop,
            'welch_p_value': p_welch,
            'mw_p_value': p_mw,
            'significant_mw': p_mw < 0.05
        })
        
    res_df = pd.DataFrame(results)
    
    print("\n Statistical Test Results (Welch's T-test and Mann-Whitney U) ")
    print(res_df.to_string(index=False))
    
    # save statistical results for Mr. D'yada
    stats_filename = 'part3_stats.csv'
    res_df.to_csv(stats_filename, index=False)
    print(f"\nResults saved to {stats_filename}")

if __name__ == "__main__":
    analyze_part3()