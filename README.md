# Clinical Trial Immune Profiling Pipeline
## Author: Bob's favorite analyst (Jadon Freed)

## Quick Start

1. **Environment Setup:** `make setup`
2. **Data Pipeline:** `make pipeline`
3. **Interactive Dashboard:** `make dashboard`

---

## Planning & Thought Process

### 1. Relational Data Modeling
My primary goal was to move away from the flat-file CSV structure to a paritioned schema using SQLite. 

It was split into three different tables:
- Subject Info: subject_id (Key), project_id, condition, age, sex, treatment, response
    - This stores demographic and clinical info about each patient 

- Sample Info: sample_id (Key), subject_id (Secondary Key), sample_type, time_from_treatment_start
    - Captures longitudinal events and allows for multiple samples from a single patient
    - Links to subject info and provides link for patient-specific lab results

- Cell count Info: sample_id (Secondary Key), population (cell type), cell_count
    - Stores lab results in long format to allow for multiple cell types without creating a significant number of columns


![Database Schema](Bobs_Database_Schema.pdf)


* Flat files lead to data redundancy and update issues. By separating data into subjects, samples, and cell_counts, we ensure that patient demographics are stored exactly once.
* I chose to store cell counts in a long format (population (Cell type) and count columns) rather than wide columns to allow for the lab to track new cell types without the database structure changing.

### 2. Statistical Methodology
To address Bob's question regarding treatment response in Melanoma patients, I implemented the **Mann-Whitney U Test**.

* **Rationale:** Since we are dealing with relative frequencies (percentages), the data is bounded (0-100) and often non-normally distributed. The Mann-Whitney U test is a non-parametric approach that provides more statistical rigor than a standard T-test for high-variance biological datasets.

### 3. Development Workflow
I utilized AI to accelerate development:
* **Boilerplate & ETL:** AI was used to generate initial Pandas `melt` logic and the CSS styling for the Dash components.
* **Manual Refinement:** I manually refactored the AI's output to ensure the dashboard dynamically queries the SQLite backend via SQL `JOIN` operations, rather than relying on static data frames. This ensures the UI remains aan accurate reflection of the database, which controls for any updates to the database system.
* **Verification:** I conducted manual spot-checks on the SQL aggregation results (e.g., average B-cell counts) against the raw CSV to verify the mathematical integrity of the automated scripts.

---

## Pipeline Scalability
If this project were to scale to hundreds of projects and thousands of subjects, I would implement the following:

### Database Partitioning
I would partition by project_id if the scale drastically increased. This allows the system to ignore irrelevant project data during a query, significantly increasing speed as the dataset grows.

### Migration to Enterprise SQL
For a production environment, I would migrate from SQLite to **PostgreSQL**. This would allow for:
* Concurrent write access from multiple lab technicians.
* Advanced indexing strategies on `subject_id` and `sample_id`.
* Integration with professional ORMs like SQLAlchemy for more robust code maintenance.

---

## File Structure
* `load_data.py`: ETL script to initialize the SQLite DB and normalize the CSV.
* `part2.py`: Generates relative frequency tables and total cell counts.
* `part3.py`: Conducts Mann-Whitney U testing and generates baseline boxplots.
* `part4.py`: Performs complex SQL joins to extract specific cohort insights.
* `dashboard.py`: A Plotly Dash application providing an interactive interface for the clinical team.
* `Makefile`: Orchestration script for grading and reproduction.

---

## Dashboard Access
Once the server is running via `make dashboard`, access the interface at:
**http://127.0.0.1:8050**