import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3


print("\nLOADING DASHBOARD")
# start dash app
app = dash.Dash(__name__)

# load and prepare data for the dashboard
def load_data():
    
    df_meta = pd.read_csv('data/cell-count.csv')[['sample', 'condition', 'treatment', 'sample_type', 'response']].drop_duplicates()
    
    df_summary = pd.read_csv('data/part2_summary.csv')
    
    return pd.merge(df_summary, df_meta, on='sample', how='inner')

df_all = load_data()


def get_bobs_insights():
    """Dynamically queries the SQLite DB for Bob's insights (currently set to the base cohort)."""
    import sqlite3
    conn = sqlite3.connect('clinical_trial.db')
    
    # base cohort definition: Melanoma, Miraclib, PBMC, time=0
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
    
    # calculate stats based on Bob's questions
    # How many samples from each project
    proj_counts = df_base.groupby('project_id')['sample_id'].nunique().to_dict()
    proj_str = " - ".join([f"{k} ({v})" for k, v in proj_counts.items()])
    
    # How many subjects were responders/non-responders
    resp_counts = df_base.groupby('response')['subject_id'].nunique().to_dict()
    resp_str = f"Responders: {resp_counts.get('yes', 0)} - Non-responders: {resp_counts.get('no', 0)}"
    
    # How many subjects were males/females
    sex_counts = df_base.groupby('sex')['subject_id'].nunique().to_dict()
    sex_str = f"Males ({sex_counts.get('M', 0)}) - Females ({sex_counts.get('F', 0)})"
    
    query_b_cells = """
        SELECT AVG(cc.cell_count) FROM cell_counts cc
        JOIN samples sa ON cc.sample_id = sa.sample_id
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma' AND su.sex = 'M' AND su.treatment = 'miraclib'
          AND su.response = 'yes' AND sa.time_from_treatment_start = 0 
          AND sa.sample_type = 'PBMC' AND cc.population = 'b_cell'
    """
    cursor = conn.cursor()
    cursor.execute(query_b_cells)
    avg_b_cells = cursor.fetchone()[0]
    avg_b_cells_str = f"{avg_b_cells:,.2f}" if avg_b_cells else "N/A"
    
    conn.close()
    return proj_str, resp_str, sex_str, avg_b_cells_str

# get the insights for the specific subset in part 4 to display on the dashboard
proj_str, resp_str, sex_str, avg_b_cells_str = get_bobs_insights()




# create the layout of the dashboard
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1("Loblaw Bio: Immune Cell Population Dashboard"),
    html.P("Interactive analysis of relative cell frequencies across various patient samples."),
    
    # dropdowns for filtering the boxplot
    html.Div([
        html.Div([
            html.Label("Select Condition:"),
            dcc.Dropdown(
                id='condition-dropdown',
                options=[{'label': c.capitalize(), 'value': c} for c in df_all['condition'].dropna().unique()],
                value='melanoma'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("Select Treatment:"),
            dcc.Dropdown(
                id='treatment-dropdown',
                options=[{'label': t.capitalize(), 'value': t} for t in df_all['treatment'].dropna().unique()],
                value='miraclib'
            )
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),
    
    # interactive boxplot adapted to dropdown filters
    dcc.Graph(id='boxplot-graph'),
    html.Hr(),
    
    
    
    # queried Stats Section for the specific subset in part 4
    html.H3("Early Treatment Effects - (Melanoma Condition, Miraclib Treatment, PBMC Sample, Baseline Timepoint)"),
    
    html.Ul([
        html.Li(f"Samples per project: {proj_str}"),
        html.Li(resp_str),
        html.Li(f"Sex distribution: {sex_str}"),
        html.Li(f"Average B cells (Melanoma Male Responders at time=0): {avg_b_cells_str}")
    ])
])

# update the graph based on dropdowns
@app.callback(
    Output('boxplot-graph', 'figure'),
    [Input('condition-dropdown', 'value'),
     Input('treatment-dropdown', 'value')]
)
def update_graph(condition, treatment):
    # filter data based on dropdown selections
    filtered = df_all[
        (df_all['condition'] == condition) & 
        (df_all['treatment'] == treatment) & 
        (df_all['sample_type'] == 'PBMC')
    ].dropna(subset=['response'])
    
    if filtered.empty:
        return px.box(title="No data available for the selected filters.")
    
    # generate Plotly figure
    fig = px.box(
        filtered, 
        x='population', 
        y='percentage', 
        color='response',
        title=f'Relative Frequencies in {condition.capitalize()} PBMC ({treatment.capitalize()}) - Responders vs Non-Responders',
        labels={'percentage': 'Relative Frequency (%)', 'population': 'Cell Population'},
        category_orders={"population": sorted(filtered['population'].unique())}
    )
    return fig

if __name__ == '__main__':
    # Run dash app by looking up (http://localhost:8050) on browser
    app.run(debug=True, host='0.0.0.0', port=8050)