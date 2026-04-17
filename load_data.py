import pandas as pd
import sqlite3
import os

def create_database():
    db_path = 'clinical_trial.db'
    csv_path = 'cell-count.csv'

    # initialize the database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    df = pd.read_csv(csv_path)

    # Schema Creation
    
    # Drop existing tables if re-running
    cursor.execute('DROP TABLE IF EXISTS cell_counts')
    cursor.execute('DROP TABLE IF EXISTS samples')
    cursor.execute('DROP TABLE IF EXISTS subjects')
    

    # Table 1: subjects
    ## table schema: subject_id (PK), project_id, condition, age, sex, treatment, response 
    cursor.execute('''
        CREATE TABLE subjects (
            subject_id TEXT PRIMARY KEY,
            project_id TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT
        )
    ''')

    # Table 2: samples
    ## table schema: sample_id (PK), subject_id (FK), sample_type, time_from_treatment_start
    cursor.execute('''
        CREATE TABLE samples (
            sample_id TEXT PRIMARY KEY,
            subject_id TEXT,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
    ''')

    # Table 3: cell_counts (long format)
    ## table schema: subject_id (PK), project_id, condition, age, sex, treatment, response
    cursor.execute('''
        CREATE TABLE cell_counts (
            sample_id TEXT,
            population TEXT,
            cell_count INTEGER,
            FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
            PRIMARY KEY (sample_id, population)
        )
    ''')

    # Data Preparation
    ## Prepares data for each table and insert into the sqlite database

    # Table 1. Subjects Table Data
    subjects_df = df[['subject', 'project', 'condition', 'age', 'sex', 'treatment', 'response']].drop_duplicates()
    subjects_df = subjects_df.rename(columns={'subject': 'subject_id', 'project': 'project_id'})
    subjects_df.to_sql('subjects', conn, if_exists='append', index=False)

    # Table 2. Samples Table Data
    samples_df = df[['sample', 'subject', 'sample_type', 'time_from_treatment_start']].drop_duplicates()
    samples_df = samples_df.rename(columns={'sample': 'sample_id', 'subject': 'subject_id'})
    samples_df.to_sql('samples', conn, if_exists='append', index=False)

    # Table 3. Cell Counts Table Data
    counts_df = df[['sample', 'b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']]
    counts_long = pd.melt(counts_df, id_vars=['sample'], var_name='population', value_name='cell_count')
    counts_long = counts_long.rename(columns={'sample': 'sample_id'})
    counts_long.to_sql('cell_counts', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    print(f"Database successfully initialized and data loaded into {db_path}")

if __name__ == "__main__":
    create_database()