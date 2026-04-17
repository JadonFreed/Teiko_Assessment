import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import levene

def check_distributions():
    # I loaded from csv for simplicity, but we could also query the SQLite database directly
    ## since it is a baseline distribution check this will suffice for initial analysis.
    df = pd.merge(
        pd.read_csv('part2_summary.csv'),
        pd.read_csv('cell-count.csv')[['sample', 'condition', 'treatment', 'response', 'sample_type']],
        on='sample'
    )
    
    # filter for the relevant cohort (Melanoma, Miraclib) and ensure that the sample type is blood (PBMC)
    df_filtered = df[(df['condition'] == 'melanoma') & (df['treatment'] == 'miraclib') & (df['sample_type'] == 'PBMC')]
    
    populations = df_filtered['population'].unique()
    
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
    plt.savefig('distribution_check.png')
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


    means.to_csv('clinical_summary_stats.csv')

if __name__ == "__main__":
    check_distributions()