from dash import html, dcc, callback, Output, Input, State, no_update
import dash
import dash.dash_table
import plotly.express as px
import pandas as pd
import os
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css', 'assets/styles2.css'])
server=app.server

# Helper functions
def normalize_col_name(col_name):
    if pd.isna(col_name):
        return ''
    return str(col_name).strip().lower().replace(' ', '_').replace('/', '_').replace('-', '_').replace('(', '').replace(')', '').replace('.', '')

def normalize_status_value(status_val):
    if pd.isna(status_val):
        return None
    return str(status_val).strip().upper()

# Expected column names mapping
EXPECTED_COLS_NORMALIZED = {
    'pillar': 'Pillar',
    'ssp_outcome': 'NST2 Outcome',
    'indicator': 'Indicators',
    'units': 'Units',
    'baseline': 'Baseline (2023/24)',
    '2024_25_target': '2024/25 target',
    '2026_27_target': '2026/27 target',
    'current_progress_2024_25': 'Current progress (2024/25)',
    'progress_based_on_2024_25_target': '% Progress based on 2024/25 Target',
    'status_based_on_2024_25_target': 'Status based on 2024/25 Target',
    'progress_based_on_2026_27_target': '% Progress based on 2026/27 Target',
    'status_based_on_2026_27_target': 'Status based on 2026/27 Target',
    'major_drivers_of_performance_maximum_2': 'Major drivers of performance (Maximum 2)',
    'challenges_if_any': 'Challenges, if any',
    'catch_up_plans': 'Catch up Plans ',
    'annual_targets_2028_29': 'Annual Targets (2028/29)',
    'responsibility_for_reporting': 'Responsibility for reporting',
    'data_sources_report': 'Data Sources (report)'
}

# Initialize data variables
initial_data = pd.DataFrame()
initial_status_data = {}
initial_pillar_options = []
data_load_message = ""
actual_col_name_map = {}

# Try to load data
try:
    df_raw = pd.read_excel('matrix.xlsx')
    df_raw['Units'] = df_raw['Units'].str.replace('Percent', '%', regex=False)
    initial_data = df_raw.copy()
    
    actual_col_name_map = {normalize_col_name(col): col for col in df_raw.columns}
    
    pillar_col = actual_col_name_map.get(normalize_col_name(EXPECTED_COLS_NORMALIZED['pillar']))
    ssp_outcome_col = actual_col_name_map.get(normalize_col_name(EXPECTED_COLS_NORMALIZED['ssp_outcome']))
    indicator_col = actual_col_name_map.get(normalize_col_name(EXPECTED_COLS_NORMALIZED['indicator']))
    status_2024_25_col = actual_col_name_map.get(normalize_col_name(EXPECTED_COLS_NORMALIZED['status_based_on_2024_25_target']))
    status_2026_27_col = actual_col_name_map.get(normalize_col_name(EXPECTED_COLS_NORMALIZED['status_based_on_2026_27_target']))
    
    essential_display_cols = [pillar_col, ssp_outcome_col, indicator_col]
    if not all(col is not None and col in initial_data.columns for col in essential_display_cols):
        missing_names = [
            EXPECTED_COLS_NORMALIZED['pillar'] if pillar_col is None or pillar_col not in initial_data.columns else None,
            EXPECTED_COLS_NORMALIZED['ssp_outcome'] if ssp_outcome_col is None or ssp_outcome_col not in initial_data.columns else None,
            EXPECTED_COLS_NORMALIZED['indicator'] if indicator_col is None or indicator_col not in initial_data.columns else None
        ]
        missing_names = [name for name in missing_names if name is not None]
        data_load_message = html.Div(
            f'Error: Missing essential columns for dashboard functionality: {", ".join(missing_names)}',
            className='info-message-error'
        )
        initial_data = pd.DataFrame()
    else:
        if status_2024_25_col and status_2024_25_col in initial_data.columns:
            initial_data[status_2024_25_col] = initial_data[status_2024_25_col].apply(normalize_status_value)
        if status_2026_27_col and status_2026_27_col in initial_data.columns:
            initial_data[status_2026_27_col] = initial_data[status_2026_27_col].apply(normalize_status_value)
        
        unique_pillars = [p for p in initial_data[pillar_col].unique() if pd.notna(p)]
        initial_pillar_options = [{'label': p, 'value': p} for p in unique_pillars]
        
        status_categories = ['COMPLETED', 'GOOD', 'SATISFACTORY', 'LOW']
        
        if status_2024_25_col and status_2026_27_col:
            for pillar in unique_pillars:
                pillar_df = initial_data[initial_data[pillar_col] == pillar]
                
                counts_2024_25 = pillar_df[status_2024_25_col].value_counts().to_dict()
                status_counts_2024_25 = {cat: counts_2024_25.get(cat, 0) for cat in status_categories}
                
                counts_2026_27 = pillar_df[status_2026_27_col].value_counts().to_dict()
                status_counts_2026_27 = {cat: counts_2026_27.get(cat, 0) for cat in status_categories}
                
                initial_status_data[pillar] = {
                    '2024/25': status_counts_2024_25,
                    '2026/7': status_counts_2026_27
                }
        else:
            data_load_message = html.Div(
                "Warning: One or both status columns are missing. Status breakdown and table will not be displayed.",
                className='info-message-warning'
            )

except FileNotFoundError:
    data_load_message = html.Div(
        "Error: Data file not found. Please ensure 'matrix.xlsx' exists.",
        className='info-message-error'
    )
except Exception as e:
    data_load_message = html.Div(
        f"An error occurred while loading or processing data: {str(e)}",
        className='info-message-error'
    )

# Hardcoded sector options
initial_sector_options = [
    'PSDYE', 'WATSAN', 'ENERGY', 'PFM', 'FSD', 'SPORT AND CULTURE',
    'AGRICULTURE', 'HEALTH', 'EDUCATION', 'ICT', 'TRANSPORT',
    'URBANISATION', 'CENR', 'JRLO', 'GOVERNANCE', 'SOCIAL PROTECTION'
]

# Main layout of the application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='uploaded-data', data=initial_data.to_dict('records') if not initial_data.empty else {}),
    dcc.Store(id='processed-status-data', data=initial_status_data),
    dcc.Store(id='dynamic-pillar-options', data=[opt['value'] for opt in initial_pillar_options]),
    
    # Header section
    html.Div([
        html.Img(src='/assets/Coat_of_arms_of_Rwanda.svg', className='header-logo'),
        html.H1("NST2 PROGRESS DASHBOARD", id='dashboard-title', className='dashboard-title-text')
    ], className='header-container'),

    # Main content wrapper
    dbc.Row(className='app-content-wrapper g-0', children=[
        # Sidebar Column
        dbc.Col(
            html.Div(id='sidebar', className='sidebar-container', children=[
                dbc.NavLink(
                    html.Button("🏠 Home", id='home-btn', n_clicks=0, className='home-button'),
                    href="/",
                    active="exact",
                    className='sidebar-nav-link'
                ),
                html.Br(),
                html.Div(id='data-load-message-display', children=data_load_message),
                
                html.Label("Select the SSP sector", className='dropdown-label'),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            html.Div("ICT Dashboard", className="ms-1"),
                            href="/ict",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("PSDYE Dashboard", className="ms-1"),
                            href="/psdye",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("CENR Dashboard", className="ms-1"),
                            href="/cenr",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Education Dashboard", className="ms-1"),
                            href="/education",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Health Dashboard", className="ms-1"),
                            href="/health",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Governance Dashboard", className="ms-1"),
                            href="/governance",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Agriculture Dashboard", className="ms-1"),
                            href="/agriculture",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Transport Dashboard", className="ms-1"),
                            href="/transport",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Social Protection Dashboard", className="ms-1"),
                            href="/social-protection",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Energy Dashboard", className="ms-1"),
                            href="/energy",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Urbanisation Dashboard", className="ms-1"),
                            href="/urbanisation",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("WATSAN Dashboard", className="ms-1"),
                            href="/watsan",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("JRLO Dashboard", className="ms-1"),
                            href="/jrlo",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("Sport and Culture Dashboard", className="ms-1"),
                            href="/sport",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("PFM Dashboard", className="ms-1"),
                            href="/pfm",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                        dbc.NavLink(
                            html.Div("FSD Dashboard", className="ms-1"),
                            href="/fsd",
                            active="exact",
                            className='sidebar-nav-link'
                        ),
                    ],
                    vertical=True,
                    pills=True,
                    className='sidebar-nav-group'
                ),
                html.Br(),
            ]),
            width=2,
            className="sidebar-col"
        ),

        # Main Content Area
        dbc.Col(
            html.Div(id='main-content-wrapper', className='main-content-wrapper', children=[
                html.Div(id='home-dashboard-content', style={'display': 'none'}, children=[
                    # Metric cards
                    html.Div([
                        html.Div([
                            html.H2(id='num-pillars-metric', className='metric-number', children="3"),
                            html.P("Number of Pillars", className='metric-label')
                        ], className='metric-card'),
                        html.Div([
                            html.H2(id='num-sectors-metric', className='metric-number', children="0"),
                            html.P("Number of Sectors", className='metric-label')
                        ], className='metric-card'),
                        html.Div([
                            html.H2(id='num-outcomes-metric', className='metric-number', children="0"),
                            html.P("Number of Outcomes", className='metric-label')
                        ], className='metric-card'),
                        html.Div([
                            html.H2(id='num-indicators-metric', className='metric-number', children="0"),
                            html.P("Number of Indicators", className='metric-label')
                        ], className='metric-card'),
                    ], className='metric-cards-container'),

                    # Pillar selection
                    html.Div([
                        html.Label("Select a Pillar", className='dropdown-label'),
                        dcc.Dropdown(
                            id='pillar-dropdown',
                            options=initial_pillar_options,
                            value=initial_pillar_options[0]['value'] if initial_pillar_options else None,
                            placeholder="Choose Pillar...",
                            className='dash-dropdown-small'
                        )
                    ], className='pillar-dropdown-container'),

                    # Integrated Pillar Subheader and Card Section
                    html.H3(id='pillar-subheader', className='pillar-subheader'),
                    html.Div(id='pillar-card-section', className='pillar-card-section'),

                    # SSP Section
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Label("Select NST2 Outcome", className='dropdown-label'),
                                dcc.Dropdown(
                                    id='home-ssp-outcome-dropdown',
                                    options=[],
                                    value=None,
                                    placeholder='Choose outcome...',
                                    className='dash-dropdown'
                                ),
                            ], className='ssp-dropdown-col'),
                            html.Div([
                                html.Label("Select Indicator", className='dropdown-label'),
                                dcc.Dropdown(
                                    id='home-ssp-indicator-dropdown',
                                    options=[],
                                    value=None,
                                    placeholder='Choose indicator...',
                                    className='dash-dropdown'
                                ),
                            ], className='ssp-dropdown-col'),
                        ], className='ssp-dropdowns-row'),

                        html.Div(id='home-indicator-detail-section', children=[
                            html.H3(id='home-selected-indicator-header', className='selected-indicator-header'),
                            html.Div(id='home-indicator-details-content')
                        ])
                    ], className='ssp-section-container')
                ]),
                
                dash.page_container
            ]),
            width=10,
            className="content-col"
        )
    ])
])

# Callbacks
@app.callback(
    Output('home-dashboard-content', 'style'),
    Input('url', 'pathname'),
    prevent_initial_call=False
)
def toggle_home_content_visibility(pathname):
    if pathname == '/':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('num-sectors-metric', 'children'),
    Input('home-btn', 'n_clicks'),
    Input('url', 'pathname'),
    prevent_initial_call=False
)
def update_num_sectors_metric(n_clicks, pathname):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered_id == 'home-btn' or pathname == '/':
        return len(initial_sector_options)
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output('dashboard-title', 'children'),
    Input('home-btn', 'n_clicks'),
    Input('url', 'pathname'),
    prevent_initial_call=False
)
def update_title(home_clicks, pathname):
    ctx = dash.callback_context
    if not ctx.triggered:
        if pathname == '/ict':
            return "ICT SSP PROGRESS DASHBOARD"
        elif pathname == '/psdye':
            return "PSDYE SSP PROGRESS DASHBOARD"
        elif pathname == '/cenr':
            return "CENR SSP PROGRESS DASHBOARD"
        elif pathname == '/education':
            return "EDUCATION SSP PROGRESS DASHBOARD"
        elif pathname == '/health':
            return "HEALTH SSP PROGRESS DASHBOARD"
        elif pathname == '/governance':
            return "GOVERNANCE SSP PROGRESS DASHBOARD"
        elif pathname == '/agriculture':
            return "AGRICULTURE SSP PROGRESS DASHBOARD"
        elif pathname == '/transport':
            return "TRANSPORT SSP PROGRESS DASHBOARD"
        elif pathname == '/social-protection':
            return "SOCIAL PROTECTION SSP PROGRESS DASHBOARD"
        elif pathname == '/energy':
            return "ENERGY SSP PROGRESS DASHBOARD"
        elif pathname == '/urbanisation':
            return "URBANISATION SSP PROGRESS DASHBOARD"
        elif pathname == '/watsan':
            return "WATSAN SSP PROGRESS DASHBOARD"
        elif pathname == '/jrlo':
            return "JRLO SSP PROGRESS DASHBOARD"
        elif pathname == '/sport':
            return "SPORT AND CULTURE SSP PROGRESS DASHBOARD"
        elif pathname == '/pfm':
            return "PFM SSP PROGRESS DASHBOARD"
        elif pathname == '/fsd':
            return "FSD SSP PROGRESS DASHBOARD"
        return "NST2 PROGRESS DASHBOARD"

    triggered_id = ctx.triggered_id
    if triggered_id == 'home-btn' or pathname == '/':
        return "NST2 PROGRESS DASHBOARD"
    elif pathname == '/ict':
        return "ICT SSP PROGRESS DASHBOARD"
    elif pathname == '/psdye':
        return "PSDYE SSP PROGRESS DASHBOARD"
    elif pathname == '/cenr':
        return "CENR SSP PROGRESS DASHBOARD"
    elif pathname == '/education':
        return "EDUCATION SSP PROGRESS DASHBOARD"
    elif pathname == '/health':
        return "HEALTH SSP PROGRESS DASHBOARD"
    elif pathname == '/governance':
        return "GOVERNANCE SSP PROGRESS DASHBOARD"
    elif pathname == '/agriculture':
        return "AGRICULTURE SSP PROGRESS DASHBOARD"
    elif pathname == '/transport':
        return "TRANSPORT SSP PROGRESS DASHBOARD"
    elif pathname == '/social-protection':
        return "SOCIAL PROTECTION SSP PROGRESS DASHBOARD"
    elif pathname == '/energy':
        return "ENERGY SSP PROGRESS DASHBOARD"
    elif pathname == '/urbanisation':
        return "URBANISATION SSP PROGRESS DASHBOARD"
    elif pathname == '/watsan':
        return "WATSAN SSP PROGRESS DASHBOARD"
    elif pathname == '/jrlo':
        return "JRLO SSP PROGRESS DASHBOARD"
    elif pathname == '/sport':
        return "SPORT AND CULTURE SSP PROGRESS DASHBOARD"
    elif pathname == '/pfm':
        return "PFM SSP PROGRESS DASHBOARD"
    elif pathname == '/fsd':
        return "FSD SSP PROGRESS DASHBOARD"
    else:
        return "NST2 PROGRESS DASHBOARD"

@app.callback(
    Output('dynamic-pillar-options', 'data'),
    Output('processed-status-data', 'data'),
    Output('pillar-dropdown', 'options'),
    Output('pillar-dropdown', 'value'),
    Output('num-outcomes-metric', 'children'),
    Output('num-indicators-metric', 'children'),
    Output('num-pillars-metric', 'children'),
    Input('uploaded-data', 'data'),
    prevent_initial_call=False
)
def update_dynamic_data_and_metrics(initial_data_dict):
    if not initial_data_dict:
        return [], {}, [], None, 0, 0, 0
        
    df = pd.DataFrame(initial_data_dict)

    num_sectors = len(initial_sector_options)
    num_outcomes = 0
    num_indicators = 0
    num_pillars = 0
    pillar_options = []
    processed_status_data = {}
    default_pillar_value = None

    if not df.empty:
        actual_pillar_col = None
        for col in df.columns:
            if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['pillar']):
                actual_pillar_col = col
                break

        if actual_pillar_col and actual_pillar_col in df.columns:
            unique_pillars = [p for p in df[actual_pillar_col].unique() if pd.notna(p)]
            num_pillars = 3
            pillar_options = [{'label': p, 'value': p} for p in unique_pillars]
            default_pillar_value = pillar_options[0]['value'] if pillar_options else None

            status_categories = ['COMPLETED', 'GOOD', 'SATISFACTORY', 'LOW']
            status_2024_25_col = None
            status_2026_27_col = None
            
            for col in df.columns:
                if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['status_based_on_2024_25_target']):
                    status_2024_25_col = col
                if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['status_based_on_2026_27_target']):
                    status_2026_27_col = col

            if status_2024_25_col and status_2026_27_col:
                for pillar in unique_pillars:
                    pillar_df = df[df[actual_pillar_col] == pillar]
                    
                    counts_2024_25 = pillar_df[status_2024_25_col].value_counts().to_dict()
                    status_counts_2024_25 = {cat: counts_2024_25.get(cat, 0) for cat in status_categories}
                    
                    counts_2026_27 = pillar_df[status_2026_27_col].value_counts().to_dict()
                    status_counts_2026_27 = {cat: counts_2026_27.get(cat, 0) for cat in status_categories}
                    
                    processed_status_data[pillar] = {
                        '2024/25': status_counts_2024_25,
                        '2026/7': status_counts_2026_27
                    }
            else:
                pass

            actual_ssp_outcome_col = None
            actual_indicator_col = None
            for col in df.columns:
                if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['ssp_outcome']):
                    actual_ssp_outcome_col = col
                if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['indicator']):
                    actual_indicator_col = col

            if actual_ssp_outcome_col:
                num_outcomes = df[actual_ssp_outcome_col].nunique()
            if actual_indicator_col:
                num_indicators = df[actual_indicator_col].nunique()

    return (
        [opt['value'] for opt in pillar_options],
        processed_status_data,
        pillar_options,
        default_pillar_value,
        num_outcomes,
        num_indicators,
        num_pillars
    )

@app.callback(
    Output('home-ssp-outcome-dropdown', 'options'),
    Output('home-ssp-outcome-dropdown', 'value'),
    Input('pillar-dropdown', 'value'),
    State('uploaded-data', 'data'),
    prevent_initial_call=False
)
def update_ssp_outcome_dropdown(selected_pillar, uploaded_data_dict):
    if not uploaded_data_dict or not selected_pillar:
        return [], None
        
    df = pd.DataFrame(uploaded_data_dict)

    if df.empty:
        return [], None

    actual_ssp_outcome_col = None
    actual_pillar_col = None
    
    for col in df.columns:
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['ssp_outcome']):
            actual_ssp_outcome_col = col
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['pillar']):
            actual_pillar_col = col

    if actual_ssp_outcome_col is None or actual_pillar_col is None:
        return [], None

    outcomes = [o for o in df[df[actual_pillar_col] == selected_pillar][actual_ssp_outcome_col].unique() if pd.notna(o)]
    options = [{'label': o, 'value': o} for o in outcomes]
    default_value = outcomes[0] if len(outcomes) > 0 else None

    return options, default_value

@app.callback(
    Output('home-ssp-indicator-dropdown', 'options'),
    Output('home-ssp-indicator-dropdown', 'value'),
    Input('home-ssp-outcome-dropdown', 'value'),
    State('uploaded-data', 'data'),
    prevent_initial_call=False
)
def update_indicator_dropdown(selected_outcome, uploaded_data_dict):
    if not uploaded_data_dict or not selected_outcome:
        return [], None
        
    df = pd.DataFrame(uploaded_data_dict)

    if df.empty:
        return [], None

    actual_indicator_col = None
    actual_ssp_outcome_col = None
    
    for col in df.columns:
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['indicator']):
            actual_indicator_col = col
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['ssp_outcome']):
            actual_ssp_outcome_col = col

    if actual_indicator_col is None or actual_ssp_outcome_col is None:
        return [], None

    indicators = [i for i in df[df[actual_ssp_outcome_col] == selected_outcome][actual_indicator_col].unique() if pd.notna(i)]
    options = [{'label': i, 'value': i} for i in indicators]
    default_value = indicators[0] if len(indicators) > 0 else None

    return options, default_value

@app.callback(
    Output('home-indicator-details-content', 'children'),
    Output('home-selected-indicator-header', 'children'),
    Input('home-ssp-indicator-dropdown', 'value'),
    State('home-ssp-outcome-dropdown', 'value'),
    State('pillar-dropdown', 'value'),
    State('uploaded-data', 'data'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def display_indicator_details(indicator, outcome, pillar, uploaded_data_dict, pathname):
    # Only proceed if we're on the home page
    if pathname != '/':
        return no_update, no_update
        
    if not uploaded_data_dict:
        return html.Div("No data available.", className='info-message-error'), ""
        
    df = pd.DataFrame(uploaded_data_dict)

    if df.empty:
        return html.Div("No data available.", className='info-message-error'), ""

    column_map = {
        'pillar': None,
        'ssp_outcome': None,
        'indicator': None,
        'units': None,
        'baseline': None,
        '2024_25_target': None,
        '2026_27_target': None,
        'current_progress_2024_25': None,
        'progress_based_on_2024_25_target': None,
        'status_based_on_2024_25_target': None,
        'progress_based_on_2026_27_target': None,
        'status_based_on_2026_27_target': None,
        'major_drivers_of_performance_maximum_2': None,
        'challenges_if_any': None,
        'catch_up_plans': None
    }

    for key in column_map:
        for col in df.columns:
            if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED[key]):
                column_map[key] = col
                break

    if not column_map['pillar'] or not column_map['ssp_outcome'] or not column_map['indicator']:
        return html.Div("Essential columns missing.", className='info-message-error'), ""

    if not outcome and column_map['pillar'] and pillar:
        outcomes = [o for o in df[df[column_map['pillar']] == pillar][column_map['ssp_outcome']].unique() if pd.notna(o)]
        if len(outcomes) > 0:
            outcome = outcomes[0]

    if not indicator and outcome and column_map['ssp_outcome']:
        indicators = [i for i in df[df[column_map['ssp_outcome']] == outcome][column_map['indicator']].unique() if pd.notna(i)]
        if len(indicators) > 0:
            indicator = indicators[0]

    if not indicator or not outcome:
        return html.Div("Please select an outcome and indicator.", className='info-message'), ""

    row = df[(df[column_map['ssp_outcome']] == outcome) & (df[column_map['indicator']] == indicator)]
    if row.empty:
        return html.Div("No data for selected combination.", className='info-message-error'), ""

    row = row.iloc[0]

    def format_value(label, value, unit=''):
        if pd.isna(value):
            return 'N/A'
        
        value_str = str(value)
        
        if ('% Progress' in label or 'Percentage Progress' in label) and '%' not in value_str:
            try:
                return f"{float(value)*100:.1f}%"
            except (ValueError, TypeError):
                return value_str
        
        if unit and label not in ['FY 2024/25 Percentage Progress', 'Mid Term NST2 Percentage Progress']:
            return f"{value_str} {unit}"
        
        return value_str

    unit_val = row.get(column_map['units'], '') if column_map['units'] else ''
    if pd.isna(unit_val):
        unit_val = ''

    metric_cards = []
    for label, col, icon in [
        ("FY 2024/25 Target", column_map['2024_25_target'], "🎯"),
        ("Mid Term NST2 Target", column_map['2026_27_target'], "📈"),
        ("Baseline", column_map['baseline'], "📊"),
        ("Current Progress (2024/25)", column_map['current_progress_2024_25'], "⏳")
    ]:
        if col and col in df.columns:
            value = row[col]
            metric_cards.append(html.Div([
                html.Div([
                    html.Div(icon, className='metric-icon'),
                    html.Div(label, className='metric-detail-label')
                ], className='metric-detail-header'),
                html.H3(
                    format_value(label, value, unit_val),
                    className='metric-detail-value'
                )
            ], className='metric-card-detail'))

    status_boxes = []
    status_class_map = {
        'COMPLETED': 'status-completed',
        'GOOD': 'status-good',
        'SATISFACTORY': 'status-satisfactory',
        'LOW': 'status-low'
    }
    
    for label, value_col, status_col, icon in [
        ("FY 2024/25 Percentage Progress", column_map['progress_based_on_2024_25_target'], 
         column_map['status_based_on_2024_25_target'], "✅"),
        ("Mid Term NST2 Percentage Progress", column_map['progress_based_on_2026_27_target'], 
         column_map['status_based_on_2026_27_target'], "➡️")
    ]:
        if value_col and status_col and value_col in df.columns and status_col in df.columns:
            value = format_value(label, row[value_col])
            status = row[status_col] if not pd.isna(row[status_col]) else "N/A"
            
            status_class = status_class_map.get(status.upper(), '') if isinstance(status, str) else ''
            
            status_boxes.append(html.Div([
                html.Div(label, className='status-box-label'),
                html.Div([
                    html.Div(value, className='status-box-value'),
                    html.Div(status.upper(), className='status-box-text')
                ], className=f'status-box-content {status_class}')
            ]))

    narrative_fields = {}
    for label, col in [
        ("Major drivers of performance", column_map['major_drivers_of_performance_maximum_2']),
        ("Challenges", column_map['challenges_if_any']),
        ("Catch up plans", column_map['catch_up_plans'])
    ]:
        if col and col in df.columns:
            value = row[col]
            narrative_fields[label] = value if not pd.isna(value) else "N/A"
        else:
            narrative_fields[label] = "N/A"

    narrative_table = html.Div([
        html.H4("Narrative Details", className='narrative-section-title'),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Major drivers of performance", className='narrative-table-header'),
                html.Th("Challenges", className='narrative-table-header'),
                html.Th("Catch up plans", className='narrative-table-header')
            ])),
            html.Tbody(html.Tr([
                html.Td(narrative_fields["Major drivers of performance"], className='narrative-table-cell'),
                html.Td(narrative_fields["Challenges"], className='narrative-table-cell'),
                html.Td(narrative_fields["Catch up plans"], className='narrative-table-cell')
            ]))
        ], className='narrative-table')
    ])

    indicator_details = html.Div([
        html.Div([
            html.Div(metric_cards[0:2], className='indicator-metric-row'),
            html.Div(metric_cards[2:4], className='indicator-metric-row'),
            html.Div(status_boxes, className='indicator-status-boxes')
        ], className='indicator-left-panel'),
        html.Div([
            narrative_table
        ], className='indicator-right-panel')
    ], className='indicator-detail-container')

    return indicator_details, f"Details for Indicator: {indicator}"

@app.callback(
    Output('pillar-subheader', 'children'),
    Output('pillar-card-section', 'children'),
    Input('pillar-dropdown', 'value'),
    State('processed-status-data', 'data'),
    State('uploaded-data', 'data'),
    prevent_initial_call=False
)
def display_pillar_dashboard(pillar, processed_status_data, uploaded_data_dict):
    if not uploaded_data_dict:
        return "No Data", html.Div("No data loaded.", className='info-message-error')
        
    df = pd.DataFrame(uploaded_data_dict)

    if df.empty:
        return "No Data", html.Div("No data loaded.", className='info-message-error')

    if not pillar:
        actual_pillar_col = None
        for col in df.columns:
            if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['pillar']):
                actual_pillar_col = col
                break
        
        if actual_pillar_col and not df.empty:
            unique_pillars = [p for p in df[actual_pillar_col].unique() if pd.notna(p)]
            if unique_pillars:
                pillar = unique_pillars[0]
        else:
            return "No Pillar Selected", html.Div("No pillars found.", className='info-message')

    # Get actual column names for calculations
    actual_ssp_outcome_col = None
    actual_indicator_col = None
    actual_pillar_col = None

    for col in df.columns:
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['ssp_outcome']):
            actual_ssp_outcome_col = col
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['indicator']):
            actual_indicator_col = col
        if normalize_col_name(col) == normalize_col_name(EXPECTED_COLS_NORMALIZED['pillar']):
            actual_pillar_col = col

    if not actual_pillar_col:
        return "No Pillar Selected", html.Div("Pillar column not found.", className='info-message-error')

    pillar_df = df[df[actual_pillar_col] == pillar]

    num_outcomes_for_pillar = 0
    if actual_ssp_outcome_col and actual_ssp_outcome_col in pillar_df.columns:
        num_outcomes_for_pillar = pillar_df[actual_ssp_outcome_col].nunique()

    num_indicators_for_pillar = 0
    if actual_indicator_col and actual_indicator_col in pillar_df.columns:
        num_indicators_for_pillar = pillar_df[actual_indicator_col].nunique()

    metric_cards_for_pillar = [
        html.Div([
            html.H2(str(num_outcomes_for_pillar), className='metric-number'),
            html.P(f"Outcomes in {pillar}", className='metric-label')
        ], className='metric-card'),
        html.Div([
            html.H2(str(num_indicators_for_pillar), className='metric-number'),
            html.P(f"Indicators in {pillar}", className='metric-label')
        ], className='metric-card')
    ]

    if pillar not in processed_status_data:
        combined_pillar_content = html.Div([
            html.Div(metric_cards_for_pillar, className='pillar-top-cards'),
            html.Div(f"No status data for {pillar}", className='info-message')
        ], className='pillar-dashboard-content')
        return f"Pillar: {pillar}", combined_pillar_content

    status_data = processed_status_data.get(pillar, {})
    status_counts_2024_25 = status_data.get('2024/25', {})
    status_counts_2026_27 = status_data.get('2026/7', {})

    # Table
    status_order = ['COMPLETED', 'GOOD', 'SATISFACTORY', 'LOW']
    table_data = []
    for status in status_order:
        table_data.append({
            'Status': status,
            '2024/25 Indicator status': status_counts_2024_25.get(status, 0),
            '2026/27 Indicator status': status_counts_2026_27.get(status, 0)
        })
    table_df = pd.DataFrame(table_data)

    status_table_component = dash.dash_table.DataTable(
        id='pillar-status-table',
        columns=[{"name": i, "id": i} for i in table_df.columns],
        data=table_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'marginBottom': '0px', 'minWidth': '100%'},
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'color': '#333'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #dee2e6'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{Status} = "COMPLETED"'},
                'backgroundColor': '#d4edda',
                'color': '#155724'
            },
            {
                'if': {'filter_query': '{Status} = "GOOD"'},
                'backgroundColor': '#d1ecf1',
                'color': '#0c5460'
            },
            {
                'if': {'filter_query': '{Status} = "SATISFACTORY"'},
                'backgroundColor': '#fff3cd',
                'color': '#856404'
            },
            {
                'if': {'filter_query': '{Status} = "LOW"'},
                'backgroundColor': '#f8d7da',
                'color': '#721c24'
            }
        ]
    )

    # Pie charts
    pie_graphs = []
    status_colors = {
        'COMPLETED': '#28a745',
        'GOOD': '#007bff',
        'SATISFACTORY': '#ffc107',
        'LOW': '#dc3545'
    }

    for year_label, counts_dict in [('2024/25', status_counts_2024_25), ('2026/27', status_counts_2026_27)]:
        pie_df = pd.DataFrame(list(counts_dict.items()), columns=['Status', 'Count'])
        pie_df = pie_df[pie_df['Count'] > 0]
        if not pie_df.empty:
            fig = px.pie(pie_df, 
                         values='Count', 
                         names='Status', 
                         title=f'Indicator Status ({year_label})',
                         color='Status',
                         color_discrete_map=status_colors,
                         hole=0.3
                        )
            fig.update_traces(textinfo='percent')
            fig.update_layout(
                margin={"l": 20, "r": 20, "t": 50, "b": 20},
                legend_title_text='Status',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#333",
                title_font_size=16,
                title_x=0.5
            )
            pie_graphs.append(dcc.Graph(figure=fig, className='pie-chart-graph'))
        else:
            pie_graphs.append(html.Div(f"No data for {year_label} status breakdown.", className='info-message-small'))

    pie_charts_layout = dbc.Row(className='g-0', children=[
        dbc.Col(
            dbc.Card(pie_graphs[0], className='h-100'),
            width=12, md=6,
            className='d-flex align-items-stretch pie-chart-col'
        ) if len(pie_graphs) > 0 else None,
        dbc.Col(
            dbc.Card(pie_graphs[1], className='h-100'),
            width=12, md=6,
            className='d-flex align-items-stretch pie-chart-col'
        ) if len(pie_graphs) > 1 else None,
        dbc.Col(
            dbc.Card(pie_graphs[0], className='h-100') if len(pie_graphs) == 1 else None,
            width=12,
            className='d-flex align-items-stretch pie-chart-col'
        ) if len(pie_graphs) == 1 else None,
    ])

    combined_pillar_content = html.Div([
        html.Div([
            html.Div(metric_cards_for_pillar, className='pillar-top-cards'),
            html.Div(status_table_component, className='status-table-container')
        ], className='pillar-left-panel'),
        html.Div([
            html.P("Status Breakdown", className='section-title'),
            pie_charts_layout
        ], className='pillar-right-panel')
    ], className='pillar-dashboard-content')

    return f"{pillar} PILLAR ", combined_pillar_content

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080)
