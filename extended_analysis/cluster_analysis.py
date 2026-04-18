import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def identify_patient_subtypes():
    print("\nUnsupervised Learning: Patient stratification (K-Means)")
    
    df_meta = pd.read_csv('data/cell-count.csv')[['sample', 'condition', 'treatment', 'response', 'sample_type']].drop_duplicates()
    df_summary = pd.read_csv('data/part2_summary.csv')
    df = pd.merge(df_summary, df_meta, on='sample', how='inner')
    
    # filter for Melanoma & Miraclib cohort, and only include PBMC samples with known response labels
    df_filtered = df[
        (df['condition'] == 'melanoma') & 
        (df['treatment'] == 'miraclib') & 
        (df['sample_type'] == 'PBMC')
    ].dropna(subset=['response'])
    
    # pivot to Wide Format and merge response labels . reset the index 
    df_wide = df_filtered.pivot(index='sample', columns='population', values='percentage').reset_index()
    df_wide = df_wide.merge(df_meta[['sample', 'response']], on='sample', how='inner')
    
    # select features
    X = df_wide.drop(columns=['sample', 'response'])
    
    # scale data 
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means Clustering
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=25)
    df_wide['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyze the Clusters (What defines each subtype?)
    print("\n1. Defining the Patient Subtypes (Mean Relative Frequencies):")
    cluster_profiles = df_wide.groupby('cluster')[X.columns].mean().round(2)
    
    # assign names based on the highest cell population in the cluster
    cluster_names = {}
    for cluster_id in cluster_profiles.index:
        dominant_cell = cluster_profiles.loc[cluster_id].idxmax()
        cluster_names[cluster_id] = f"Subtype {cluster_id} ({dominant_cell}-dominant)"
    
    cluster_profiles.index = cluster_profiles.index.map(cluster_names)
    print(cluster_profiles.to_string())
    
    # Relevance (Does a subtype predict response?)
    print("\n2. Treatment Response by Immune Subtype:")
    df_wide['cluster_name'] = df_wide['cluster'].map(cluster_names)
    response_crosstab = pd.crosstab(df_wide['cluster_name'], df_wide['response'], normalize='index') * 100
    response_crosstab = response_crosstab.round(1).astype(str) + '%'
    print(response_crosstab.to_string())
    
    # save cluster assignments for potential downstream analysis
    df_wide.to_csv('data/patient_subtypes.csv', index=False)
    print("\nSubtyping complete. Assignments saved to data/patient_subtypes.csv.")

if __name__ == "__main__":
    identify_patient_subtypes()