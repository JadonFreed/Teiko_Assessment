import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import levene

def analysis_testing():
    print("\n Part 3a: Exploratory Data Analysis and Statistical Testing")
    # I loaded from csv for simplicity, but we could also query the SQLite database directly
    ## since it is a baseline distribution check this will suffice for initial analysis.
    df_meta = pd.read_csv('data/cell-count.csv')[
        ['sample', 'condition', 'treatment', 'sample_type', 'response']
    ].drop_duplicates()
    
    # load relative frequencies from Part 2
    df_summary = pd.read_csv('data/part2_summary.csv')
    
    # merge data with frequencies
    df_merged = pd.merge(df_summary, df_meta, on='sample', how='inner')
    
    # filter criteria: melanoma, miraclib, sample is PBMC
    # filter for the relevant cohort (Melanoma, Miraclib) and ensure that the sample type is blood (PBMC)
    df_filtered = df_merged[
        (df_merged['condition'] == 'melanoma') &
        (df_merged['treatment'] == 'miraclib') &
        (df_merged['sample_type'] == 'PBMC')
    ].copy()
    
    # drop rows without a valid response label
    df_filtered = df_filtered.dropna(subset=['response'])
    
    populations = df_filtered['population'].unique()

   # distribution analysis (check normality and constant variance)
    fig, axes = plt.subplots(len(populations), 2, figsize=(12, 4 * len(populations)))
    
    for i, pop in enumerate(populations):
        pop_subset = df_filtered[df_filtered['population'] == pop]
        data = pop_subset['percentage']
        
        # check distribution 
        sns.histplot(data, kde=True, ax=axes[i, 0], color='skyblue')
        axes[i, 0].set_title(f'{pop} Distribution')
        
        # Q-Q Plot to  check normality 
        stats.probplot(data, dist="norm", plot=axes[i, 1])
        axes[i, 1].set_title(f'{pop} Q-Q Plot')
        
        # normality Check (Shapiro-Wilk) 
        ## not very informative typically, as it is a very sensitive test
        _, p_norm = stats.shapiro(data)
        norm_status = 'Normal' if p_norm > 0.05 else 'Non-Normal'
        print(f"{pop:12} - Shapiro p-value: {p_norm:.4f} ({norm_status})")
        
        # levenes constant variance test
        ## split into resp vs nonresponders to compare their variances
        responders = pop_subset[pop_subset['response'] == 'yes']['percentage']
        non_responders = pop_subset[pop_subset['response'] == 'no']['percentage']
        
        if not responders.empty and not non_responders.empty:
            _, p_levene = stats.levene(responders, non_responders)
            var_status = 'Equal Variance' if p_levene > 0.05 else 'Unequal Variance'
            print(f"{pop:12} - Levene p-value:  {p_levene:.4f} ({var_status})")
        else:
            print(f"{pop:12} - Levene Test: Insufficient data for groups")

    plt.tight_layout()
    plt.savefig('figures/distribution_check.png')
    print("Distribution plots saved as distribution_check.png")
    
    
    # SUMMARY STATISTICS FOR CELL POPULATIONS BETWEEN RESPOINDERS AND NON-RESPONDERS
    print("\nSummary Statistics (Responders vs Non-Responders)")
    
    desc_stats = df_filtered.groupby(['population', 'response'])['percentage'].agg(
        ['count', 'mean', 'std', 'median', 'min', 'max']
    ).round(3)
    
    print(desc_stats)

    # calculate effect size
    means = df_filtered.groupby(['population', 'response'])['percentage'].mean().unstack()
    means['absolute_diff'] = (means['yes'] - means['no']).round(3)
    means['percent_change'] = ((means['yes'] - means['no']) / means['no'] * 100).round(2)
    
    print("\n Mean Differences & Relative Changes (Responders vs Non-Responders)")
    print(means[['no', 'yes', 'absolute_diff', 'percent_change']].rename(
        columns={'no': 'Mean (Non-Resp)', 'yes': 'Mean (Resp)', 'absolute_diff': 'Delta (%)'}
    ))

    means.to_csv('data/clinical_summary_stats.csv')
    print("Summary statistics saved to data/clinical_summary_stats.csv")

    
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
    plot_filename = 'figures/part3_boxplot.png'
    plt.savefig(plot_filename)
    print(f"\nBoxplot saved successfully to {plot_filename}")

    # Statistical Analysis
    ## this section is motivated from a simple analysis on the distribution of the data and the variances between responders and non-responders.
    ## reference the analysis in part3_analysis.py for more details.
    results = []
    
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
    ## these will also motivate our feature selection in the predictive modeling section
    stats_filename = 'data/part3_stats.csv'
    res_df.to_csv(stats_filename, index=False)
    print(f"\nResults saved to {stats_filename}")

if __name__ == "__main__":
    analysis_testing()