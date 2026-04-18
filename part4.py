import sqlite3
import pandas as pd

def analyze_part4():
    print("\nPART 4: DATA SUBSET ANALYSIS")
    db_path = 'clinical_trial.db'
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    print("Part 4: Data Subset Analysis")

    # base query: Melanoma, Miraclib, PBMC, time=0

    base_query = """
        SELECT sa.sample_id, su.subject_id, su.project_id, su.response, su.sex
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma' 
          AND su.treatment = 'miraclib' 
          AND sa.sample_type = 'PBMC' 
          AND sa.time_from_treatment_start = 0
    """
    df_base = pd.read_sql_query(base_query, conn)
    
    # Bob's questions about specific subsets:
    
    # 1. How many samples from each project
    print("\n 1. Samples from each project:")
    project_counts = df_base.groupby('project_id')['sample_id'].nunique().reset_index(name='sample_count')
    print(project_counts.to_string(index=False))

    # 2. How many subjects were responders/non-responders
    print("\n 2. Subjects who were responders/non-responders:")
    response_counts = df_base.groupby('response')['subject_id'].nunique().reset_index(name='subject_count')
    print(response_counts.to_string(index=False))

    # 3. How many subjects were males/females
    print("\n  3. Subjects who were males/females:")
    sex_counts = df_base.groupby('sex')['subject_id'].nunique().reset_index(name='subject_count')
    print(sex_counts.to_string(index=False))

    # part 4 question : Average B Cells (Melanoma Male Responders at t=0)
    query_b_cells = """
        SELECT AVG(cc.cell_count) as avg_b_cells
        FROM cell_counts cc
        JOIN samples sa ON cc.sample_id = sa.sample_id
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND su.sex = 'M'
          AND su.treatment = 'miraclib'
          AND su.response = 'yes'
          AND sa.time_from_treatment_start = 0
          AND sa.sample_type = 'PBMC'
          AND cc.population = 'b_cell'
    """
    cursor = conn.cursor()
    cursor.execute(query_b_cells)
    
    # get first col of first row which is the average b cell count
    avg_b_cells = cursor.fetchone()[0]
    
    if avg_b_cells is not None:
        # round to 2 decismal places 
        print(f"\n4. Average number of B cells for Melanoma male responders at time=0: {avg_b_cells:.2f}")
    else:
        print("\n4. Average number of B cells for Melanoma male responders at time=0: N/A (no data)")

    conn.close()

if __name__ == "__main__":
    analyze_part4()