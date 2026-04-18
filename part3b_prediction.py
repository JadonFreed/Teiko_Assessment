import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler

def logistic_regression_model():
    print("\nBaseline Predictive Model: Logistic Regression")
    
    df_meta = pd.read_csv('data/cell-count.csv')[['sample', 'response', 'condition', 'treatment']].drop_duplicates()
    df_summary = pd.read_csv('data/part2_summary.csv')
    df = pd.merge(df_summary, df_meta, on='sample')
    
    # Filter for Bob's cohort
    df_filtered = df[(df['condition'] == 'melanoma') & (df['treatment'] == 'miraclib')]
    
    # pivot so populations are columns (Features)
    X = df_filtered.pivot(index='sample', columns='population', values='percentage')
    y = df_filtered.groupby('sample')['response'].first().map({'yes': 1, 'no': 0})
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # scaling & LR model
    scaler = StandardScaler()
    model = LogisticRegression()
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model.fit(X_train_scaled, y_train)
    
    # evaluation
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    
    print("Logistic Regression Performance:")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {auc:.3f}")
    print(f"PR-AUC Score:  {pr_auc:.3f}")
    
    # feature Importance
    importance = pd.DataFrame({'Feature': X.columns, 'Coefficient': model.coef_[0]})
    print("\nfeature Importance (Coefficients)")
    print(importance.sort_values(by='Coefficient', ascending=False))
    
    return auc, pr_auc

def random_forest_model():
    print("\n Random Forest Model with Grid Search and Cross-Validation")
    
    df_meta = pd.read_csv('data/cell-count.csv')[['sample', 'condition', 'treatment', 'response', 'sample_type', 'age', 'sex']].drop_duplicates()
    df_summary = pd.read_csv('data/part2_summary.csv')
    df = pd.merge(df_summary, df_meta, on='sample', how='inner')
    
    # Filter
    df_filtered = df[(df['condition'] == 'melanoma') & (df['treatment'] == 'miraclib') & (df['sample_type'] == 'PBMC')].dropna(subset=['response'])
    
    # Pivot
    df_wide = df_filtered.pivot(index='sample', columns='population', values='percentage').reset_index()
    df_wide = df_wide.merge(df_meta[['sample', 'response', 'age', 'sex']], on='sample', how='inner')
    
    # encode Sex as a binary feature (1 for M, 0 for F)
    df_wide['is_male'] = (df_wide['sex'] == 'M').astype(int)
    
    # FEATURE SELECTION
    X = df_wide[['b_cell', 'cd4_t_cell', 'monocyte', 'nk_cell', 'cd8_t_cell','age', 'is_male']]
    y = df_wide['response'].map({'yes': 1, 'no': 0})
    
    # grid search for optimal hyperparameters
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 4, 5, 6],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    # Initialize the base model in grid
    base_rf = RandomForestClassifier(random_state=17, class_weight='balanced')

    # set up grid search with stratified K-Fold
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=17)
    grid_search = GridSearchCV(
        estimator=base_rf, 
        param_grid=param_grid, 
        cv=cv, 
        scoring='roc_auc',
        n_jobs=-1 
    )

    grid_search.fit(X, y)

    # extract the best RF model
    best_rf = grid_search.best_estimator_
    print(f"Best Parameters: {grid_search.best_params_}")
    print(f"Best Cross-Validated ROC-AUC: {grid_search.best_score_:.3f}")
        
    
    # Evaluating both ROC-AUC and PR-AUC
    scoring = {'roc_auc': 'roc_auc', 'pr_auc': 'average_precision'}
    cv_scores = cross_validate(best_rf, X, y, cv=cv, scoring=scoring)
    
    mean_roc = np.mean(cv_scores['test_roc_auc'])
    std_roc = np.std(cv_scores['test_roc_auc'])
    mean_pr = np.mean(cv_scores['test_pr_auc'])
    std_pr = np.std(cv_scores['test_pr_auc'])
    
    print(f"Cross-Validated ROC-AUC: {mean_roc:.3f} (+/- {std_roc:.3f})")
    print(f"Cross-Validated PR-AUC:  {mean_pr:.3f} (+/- {std_pr:.3f})")
    
    # feature Importance
    best_rf.fit(X, y)
    importance = pd.DataFrame({'Feature': X.columns, 'Importance': best_rf.feature_importances_})
    print("\n RF Feature Importance")
    print(importance.sort_values(by='Importance', ascending=False).to_string(index=False))
    
    return mean_roc, mean_pr

if __name__ == "__main__":
    # run the models and store metrics
    base_roc, base_pr = logistic_regression_model()
    adv_roc, adv_pr = random_forest_model()
    
    # display the final comparison table
    print("        MODEL PERFORMANCE (Logistic Regression and Random Forest)       ")
    print(f" 1. Baseline Logistic Regression  | ROC-AUC: {base_roc:.3f} | PR-AUC: {base_pr:.3f}")
    print(f" 2. Random Forest (Grid Search/CV) | ROC-AUC: {adv_roc:.3f} | PR-AUC: {adv_pr:.3f}")
    
    # calculate performance delta
    roc_delta = adv_roc - base_roc
    pr_delta = adv_pr - base_pr

    print(f" Performance Delta                | ROC-AUC: {roc_delta:+.3f} | PR-AUC: {pr_delta:+.3f}")