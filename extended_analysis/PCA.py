import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_pca_analysis():
    print("\n--- Running Principal Component Analysis (PCA) ---")
    
    # 1. Load Data
    df_meta = pd.read_csv('data/cell-count.csv')[['sample', 'condition', 'treatment', 'response', 'sample_type']].drop_duplicates()
    df_summary = pd.read_csv('data/part2_summary.csv')
    df = pd.merge(df_summary, df_meta, on='sample', how='inner')
    
    # Filter for Melanoma & Miraclib cohort
    df_filtered = df[(df['condition'] == 'melanoma') & (df['treatment'] == 'miraclib') & (df['sample_type'] == 'PBMC')].dropna(subset=['response'])
    
    # pivot the data to Wide Format (Rows = Samples, Columns = Cell Populations)
    df_wide = df_filtered.pivot(index='sample', columns='population', values='percentage')
    
    # Re-attach the 'response' label for coloring the plot
    df_wide = df_wide.merge(df_meta[['sample', 'response']], on='sample', how='inner')
    
    # separate features (X) and labels (y)
    X = df_wide.drop(columns=['sample', 'response'])
    y = df_wide['response']
    
    # scale data before PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform PCA (Reduce 5 dimensions to 2)
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(X_scaled)
    
    # create df for pca output
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    pca_df['Response'] = y.values
    
    # calculate explained variance
    var_explained = pca.explained_variance_ratio_
    print(f"Variance explained by PC1: {var_explained[0]*100:.1f}%")
    print(f"Variance explained by PC2: {var_explained[1]*100:.1f}%")
    
    # visualize the PCA
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        x='PC1', y='PC2', 
        hue='Response', 
        palette={'yes': '#2ca02c', 'no': '#d62728'},
        data=pca_df, 
        alpha=0.7
    )
    
    plt.title('PCA of Immune Cell Frequencies (Melanoma Baseline)')
    plt.xlabel(f'Principal Component 1 ({var_explained[0]*100:.1f}% Variance)')
    plt.ylabel(f'Principal Component 2 ({var_explained[1]*100:.1f}% Variance)')
    plt.legend(title='Treatment Response')
    
    plt.tight_layout()
    plt.savefig('figures/pca_plot.png')
    print("PCA visualization saved to figures/pca_plot.png")

if __name__ == "__main__":
    run_pca_analysis()