# Clinical Trial Immune Profiling Pipeline
## Author: Bob's favorite analyst (Jadon Freed)

## Startup Instructions

1. **Environment Setup:** `make setup`
2. **Data Pipeline:** `make pipeline`
3. **Interactive Dashboard:** `make dashboard`


## File Structure
* `load_data.py`: ETL script to initialize the SQLite DB and normalize the CSV.
* `part2.py`: Generates relative frequency tables and total cell counts.
* `part3a_analysis.py`: Conducts distributional analysis and hypothesis testing (Mann-Whitney U, Welch's, and FDR correction).
* `part3b_prediction.py`: Executes predictive machine learning models (Logistic Regression vs. Tuned Random Forest).
* `part4.py`: Performs complex SQL joins to extract specific cohort insights.
* `dashboard.py`: A Plotly Dash application providing an interactive interface for the clinical team.
* `cluster_analysis.py`: K-means clustering for immune -profile type ** extended analysis
* `PCA.py`: perform PCA and select 2 top PC components ** extended analysis
* `Makefile`: Script for reproduction. 


## Dashboard Access
Once the server is running via `make dashboard`, access the interface at:
**http://127.0.0.1:8050**


## Planning & Thought Process

### Data Modeling and Schema
My primary goal was to move away from the one-table CSV structure to a paritioned schema using SQLite. 

It was split into three different tables:
Table 1 -  Subject Info: subject_id (Key), project_id, condition, age, sex, treatment, response
    - This stores demographic and clinical info about each patient 

Table 2 - Sample Info: sample_id (Key), subject_id (Secondary Key), sample_type, time_from_treatment_start
    - Captures longitudinal events and allows for multiple samples from a single patient
    - Links to subject info and provides link for patient-specific lab results

Table 3 - Cell count Info: sample_id (Secondary Key), population (cell type), cell_count
    - Stores lab results in long format to allow for multiple cell types without creating a significant number of columns

![Database Schema](figures/Bobs_Database_Schema.pdf)

* Flat files lead to data redundancy and update issues. By separating data into subjects, samples, and cell_counts, we ensure that patient demographics are stored exactly once.
* I chose to store cell counts in a long format (population (Cell type) and count columns) rather than wide columns to allow for the lab to track new cell types without the database structure changing.

### Statistical Methodology
To address Bob's question regarding treatment response in Melanoma patients, I conducted the following statistical analyses:

#### Distribution Analysis and Hypothesis Testing
- I first loaded in the data and did simple distributional analysis as well as creating some summary statistics on the groups that Bob wants to compare. 
Distribution of cell types visuals and graphs:
- Histograms: relatively normal with some slight skew
- QQ-plots: b cells and nk cells seem to diverge from typical residual tail behavior (likely non-normal), monocytes and cd8 seem to follow normal.
- Shapiro wilkes: all fail, but its known to be a very sensitive test.
- levenes test for constant variance: all fail except cd4 cells. 


This suggests using either a non-parametric test or parametric test (given unequal variances)
- Non-parametric test: Mann-whitney test - allows rank based testing (robust to outliers)
- parametric: Welch's T -test (t test for unequal variances): motivated by large sample size and CLT giving normality
- We control for multiple testing via the Benjamini-hochberg procedure to control for FDR
 

### Predictive Modeling 
To utilize this data for predictive purposes (determining treatment response):
- Logistic regression base model.
- Random Forest hyperparameters selected via a grid search with cross validation.

## Pipeline Scalability
If this project were to scale to hundreds of projects and thousands of subjects, I would implement the following:

### Database Partitioning
I would partition by project_id if the scale drastically increased. This allows the system to ignore irrelevant project data during a query, significantly increasing speed as the dataset grows. 

Transitioning the backend from SQLite to PostgreSQL to support concurrent write access and advanced indexing would help when data grows significantly. 

