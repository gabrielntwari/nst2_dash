# Modified watsan.py
# from dash import Dash, html, dcc, Input, Output # Removed Dash import as it's not needed here
from dash import html, dcc, Input, Output # Only import necessary components
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import dash

dash.register_page(__name__, path='/watsan', name='WATSAN Dashboard')

# Load and clean your dataset
try:
    df = pd.read_excel('watsan.xlsx') # Changed to watsan.xlsx
    df['Units'] = df['Units'].str.replace('Percent', '%', regex=False)
    # Data cleaning
    df = df.dropna(subset=['Outcome'])  # Remove rows with null Outcomes
    df['Outcome'] = df['Outcome'].astype(str).str.strip()  # Convert to string and strip whitespace
    df = df[df['Outcome'] != '']  # Remove empty strings
except FileNotFoundError:
    print("Error: watsan.xlsx file not found. Using empty DataFrame.") # Changed file name in error message
    df = pd.DataFrame()

# Process data for dashboard
outcomes = [o for o in df['Outcome'].unique().tolist() if o and str(o).strip()]
indicators_by_outcome = df.groupby('Outcome')['Indicators'].apply(list).to_dict()

# Calculate status counts for pie charts
status_2024_counts = df['Status based on 2024/25 Target'].value_counts().to_dict()
status_midterm_counts = df['Status based on NST2 Midterm target'].value_counts().to_dict()

# Fill missing status categories with 0
all_statuses = ['GOOD', 'SATISFACTORY', 'COMPLETED', 'LOW']
status_2024_counts = {status: status_2024_counts.get(status, 0) for status in all_statuses}
status_midterm_counts = {status: status_midterm_counts.get(status, 0) for status in all_statuses}

# Calculate summary statistics
total_outcomes = len(outcomes)
total_indicators = len(df)
avg_progress_2024 = df['Percentage Progress based on 2024/25 Target'].mean()
avg_progress_midterm = df['Percentage Progress based on 2026/27 Target'].mean()

def pie_chart(data, title):
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        hole=0.3,
        marker_colors=['red','#28a745', '#ffc107', '#17a2b8'],
        textinfo='percent',
        insidetextorientation='radial'
    )])
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        height=300,
        margin=dict(t=50, b=0, l=20, r=20),
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.5,
            xanchor="center",
            x=1
        ),
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )
    return fig

def create_progress_bar(value, label):
    color = "success" if value >= 80 else "warning" if value >= 50 else "danger"
    return dbc.Card([
        dbc.CardHeader(label, className='progress-header', style={'font-weight': 'bold'}),
        dbc.CardBody([
            dbc.Progress(value=value, color=color, className="mb-3", style={'height': '20px'}),
            html.Div(f"{value:.1f}%", className="progress-value", style={
                'text-align': 'center',
                'font-weight': 'bold',
                'font-size': '1.1rem'
            })
        ])
    ], className='progress-card', style={'height': '100%'})

def generate_summary_points():
    summary_points = []
    
    summary_points.append(
        html.Li(["Significant progress from 2017–2024, including increased water production capacity (from ",
            html.Span("182,120", className="highlight-number"),
            " to ",
            html.Span("329,652 m³/day", className="highlight-number"),
            ") and expansion of the water distribution network to ",
            html.Span("33,476 km", className="highlight-number"),
            "."
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["Clean water access reached ",
            html.Span("82.3%", className="highlight-percent"),
            " nationally by 2022, with urban areas at ",
            html.Span("96%", className="highlight-percent"),
            " and rural areas at ",
            html.Span("77%", className="highlight-percent"),
            ", revealing ongoing disparities."
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["Sanitation improvements include ",
            html.Span("92%", className="highlight-percent"),
            " of households using improved toilets and new sewage and faecal sludge treatment systems in Kigali and other districts."
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["Persistent challenges remain, such as limited financing, high Non-Revenue Water (only reduced from ",
            html.Span("42%", className="highlight-percent"),
            " to ",
            html.Span("39%", className="highlight-percent"),
            "), and project delays due to institutional and climate-related factors."
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["Strategic goals for ",
            html.Span("2029", className="highlight-number"),
            " include ",
            html.Span("100%", className="highlight-percent"),
            " access to clean water and sanitation, expanding water production to ",
            html.Span("684,652 m³/day", className="highlight-number"),
            ", completing Kigali’s sewerage system, and enhancing waste management."
        ], className="summary-point")
    )
    
    return summary_points

# Layout
layout = html.Div([
    dcc.Location(id='url-watsan', refresh=False), # Unique ID
    
    html.Div(id='page-content-watsan', children=[ # Unique ID
        html.Div(className='main-content-wrapper', children=[
            
            # # 1. Header Section
            # html.Div(className='dashboard-header', children=[
            #     html.H1("WATSAN SSP PROGRESS DASHBOARD", className='dashboard-title'), # Changed title
            #     html.Div(className='dashboard-subtitle', children="Comprehensive Overview of Sector Performance and Progress")
            # ]),
            
            # 2. Top Row - Metrics and Summary
            dbc.Row(className='top-row', children=[
                # Metrics Cards
                dbc.Col(className='metrics-col', width=3, children=[
                    dbc.Row([
                        # Total Outcomes Card
                        dbc.Col(dbc.Card([
                            dbc.CardHeader(html.Div("TOTAL OUTCOMES", className="metric-header"), 
                                         style={'background': 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)'}),
                            dbc.CardBody([
                                html.Div(str(total_outcomes), className="metric-number",
                                        style={'color': '#6a11cb', 'text-shadow': '0 2px 4px rgba(106,17,203,0.3)'}),
                                html.Div([
                                    html.I(className="fas fa-chart-line metric-icon"),
                                    ""
                                ], className="metric-label"),
                            ], style={'text-align': 'center'})
                        ], className='metric-card', style={
                            'border': 'none',
                            'border-radius': '12px',
                            'box-shadow': '0 6px 15px rgba(106,17,203,0.2)',
                            'transition': 'transform 0.3s',
                            'margin-bottom': '20px'
                        }), width=12),
                        
                        # Total Indicators Card
                        dbc.Col(dbc.Card([
                            dbc.CardHeader(html.Div("TOTAL INDICATORS", className="metric-header"), 
                                         style={'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'}),
                            dbc.CardBody([
                                html.Div(str(total_indicators), className="metric-number",
                                        style={'color': '#11998e', 'text-shadow': '0 2px 4px rgba(17,153,142,0.3)'}),
                                html.Div([
                                    html.I(className="fas fa-tasks metric-icon"),
                                    ""
                                ], className="metric-label"),
                            ], style={'text-align': 'center'})
                        ], className='metric-card', style={
                            'border': 'none',
                            'border-radius': '12px',
                            'box-shadow': '0 6px 15px rgba(17,153,142,0.2)',
                            'transition': 'transform 0.3s'
                        }), width=12)
                    ], style={'height': '30%'})
                ]),
                
                # Summary Card
                dbc.Col(className='summary-col', width=9, children=[
                    dbc.Card(className='summary-card', children=[
                        dbc.CardHeader(
                            html.Div([
                                html.I(className="fas fa-chart-pie me-2"),
                                "SECTOR PERFORMANCE HIGHLIGHTS"
                            ]), 
                            className='summary-header',
                            style={
                                'background': 'linear-gradient(135deg, #2b5876 0%, #4e4376 100%)',
                                'color': 'white',
                                'font-size': '1.1rem',
                                'font-weight': '600',
                                'letter-spacing': '0.5px',
                                'border-radius': '12px 12px 0 0'
                            }
                        ),
                        dbc.CardBody([
                            html.Ul(generate_summary_points(), className="summary-list", style={
                                'padding-left': '20px',
                                'list-style-type': 'none'
                            })
                        ], style={
                            'background': 'rgba(248, 249, 250, 0.7)',
                            'border-radius': '0 0 12px 12px',
                            'padding': '20px'
                        })
                    ], style={
                        'border': 'none',
                        'border-radius': '12px',
                        'box-shadow': '0 10px 20px rgba(0,0,0,0.1)',
                        'height': '100%',
                        'background': 'white'
                    })
                ])
            ], style={'margin-bottom': '25px'}),
            
            # 3. Status Section (Table and Pie Charts)
            dbc.Row(className='status-section', children=[
                # Status Table
                dbc.Col(className='table-col', width=4, children=[
                    dbc.Card([
                        dbc.CardHeader("INDICATOR STATUS", className='table-header', 
                                      style={'background-color': '#343a40', 'color': 'white', 
                                             'font-weight': 'bold', 'padding': '10px',
                                             'border-radius': '8px 8px 0 0'}),
                        dbc.CardBody([
                            dbc.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Status", style={'width': '40%', 'text-align': 'left'}),
                                        html.Th("Indicator Status based on 2024/25 Target", style={'width': '30%', 'text-align': 'center'}),
                                        html.Th("Indicator Status based on MidTerm Target", style={'width': '30%', 'text-align': 'center'})
                                    ], style={'background-color': '#f8f9fa'})
                                ]),
                                html.Tbody([
                                    html.Tr([
                                        html.Td("GOOD", className='status-cell good', 
                                              style={'font-weight': 'bold', 'text-align': 'left'}),
                                        html.Td(status_2024_counts.get('GOOD', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'}),
                                        html.Td(status_midterm_counts.get('GOOD', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'})
                                    ], style={'border-bottom': '1px solid #dee2e6'}),
                                    html.Tr([
                                        html.Td("SATISFACTORY", className='status-cell satisfactory',
                                              style={'font-weight': 'bold', 'text-align': 'left'}),
                                        html.Td(status_2024_counts.get('SATISFACTORY', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'}),
                                        html.Td(status_midterm_counts.get('SATISFACTORY', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'})
                                    ], style={'border-bottom': '1px solid #dee2e6'}),
                                    html.Tr([
                                        html.Td("COMPLETED", className='status-cell completed',
                                              style={'font-weight': 'bold', 'text-align': 'left'}),
                                        html.Td(status_2024_counts.get('COMPLETED', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'}),
                                        html.Td(status_midterm_counts.get('COMPLETED', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'})
                                    ], style={'border-bottom': '1px solid #dee2e6'}),
                                    html.Tr([
                                        html.Td("LOW", className='status-cell low',
                                              style={'font-weight': 'bold', 'text-align': 'left'}),
                                        html.Td(status_2024_counts.get('LOW', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'}),
                                        html.Td(status_midterm_counts.get('LOW', 0), 
                                              style={'text-align': 'center', 'font-weight': 'bold'})
                                    ])
                                ])
                            ], bordered=False, hover=True, responsive=True,
                            style={
                                'margin-bottom': '0',
                                'width': '100%',
                                'border': '1px solid #dee2e6',
                                'border-radius': '0 0 8px 8px'
                            },
                            className="table-striped")
                        ], style={'padding': '0'})
                    ], style={
                        'height': '100%',
                        'border': 'none',
                        'border-radius': '8px',
                        'box-shadow': '0 4px 6px rgba(0,0,0,0.1)'
                    })
                ]),
                
                # Pie Charts
                dbc.Col(className='pie-col', width=4, children=[
                    dcc.Graph(
                        figure=pie_chart(status_2024_counts, "2024/25 Target Status"),
                        className='pie-chart',
                        style={'height': '100%'}
                    )
                ]),
                dbc.Col(className='pie-col', width=4, children=[
                    dcc.Graph(
                        figure=pie_chart(status_midterm_counts, "MidTerm Target Status"),
                        className='pie-chart',
                        style={'height': '100%'}
                    )
                ])
            ], style={'margin-bottom': '20px', 'align-items': 'stretch'}),
            
            # 4. Selection Section
            dbc.Row(className='selection-section', children=[
                dbc.Col(width=6, children=[
                    html.Label("SELECT OUTCOME", className="dropdown-label",
                             style={'font-weight': 'bold', 'margin-bottom': '5px'}),
                    dcc.Dropdown(
                        id='watsan-outcome-dropdown', # Unique ID
                        options=[{'label': o, 'value': o} for o in outcomes if o and str(o).strip()],
                        value=outcomes[0] if outcomes else None,
                        className='outcome-dropdown',
                        style={'border-radius': '4px', 'border': '1px solid #ced4da'}
                    )
                ]),
                dbc.Col(width=6, children=[
                    html.Label("SELECT INDICATOR", className="dropdown-label",
                              style={'font-weight': 'bold', 'margin-bottom': '5px'}),
                    dcc.Dropdown(
                        id='watsan-indicator-dropdown', # Unique ID
                        className='indicator-dropdown',
                        style={'border-radius': '4px', 'border': '1px solid #ced4da'}
                    )
                ])
            ], style={'margin-bottom': '20px'}),
            
            # 5. Indicator Metrics and Narrative
            dbc.Row(className='indicator-narrative-section', children=[
                # Indicator Metrics
                dbc.Col(className='indicator-metrics-col', width=4, children=[
                    dbc.Row([
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("Baseline", className='indicator-header',
                                          style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                            dbc.CardBody([
                                html.Div(id='watsan-baseline-value', className="indicator-value", # Unique ID
                                        style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                            ])
                        ], className='indicator-card'), width=6),
                        
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("2024/25 Target", className='indicator-header',
                                          style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                            dbc.CardBody([
                                html.Div(id='watsan-target-2024-value', className="indicator-value", # Unique ID
                                        style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                            ])
                        ], className='indicator-card'), width=6)
                    ], style={'margin-bottom': '15px'}),
                    dbc.Row([
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("2026/27 Target", className='indicator-header',
                                          style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                            dbc.CardBody([
                                html.Div(id='watsan-target-midterm-value', className="indicator-value", # Unique ID
                                        style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                            ])
                        ], className='indicator-card'), width=6),
                        
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("Current Progress", className='indicator-header',
                                          style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                            dbc.CardBody([
                                html.Div(id='watsan-current-value', className="indicator-value", # Unique ID
                                        style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                            ])
                        ], className='indicator-card'), width=6)
                    ], style={'margin-bottom': '15px'}),
                    # Progress Bars
                    dbc.Row([
                        dbc.Col(html.Div(id='watsan-progress-2024'), width=6), # Unique ID
                        dbc.Col(html.Div(id='watsan-progress-midterm'), width=6) # Unique ID
                    ])
                ]),
                
                # Narrative Table
                dbc.Col(className='narrative-col', width=8, children=[
                    dbc.Card([
                        dbc.CardHeader("Narrative Section", className='narrative-header',
                                      style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            dbc.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Major drivers of performance", className='narrative-th',
                                               style={'background-color': '#343a40', 'color': 'white'}),
                                        html.Th("Challenges", className='narrative-th',
                                               style={'background-color': '#343a40', 'color': 'white'}),
                                        html.Th("Catch up plans", className='narrative-th',
                                               style={'background-color': '#343a40', 'color': 'white'})
                                    ])
                                ]),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(id='watsan-drivers-text', className='narrative-td', # Unique ID
                                              style={'vertical-align': 'top', 'border-right': '1px solid #dee2e6'}),
                                        html.Td(id='watsan-challenges-text', className='narrative-td', # Unique ID
                                              style={'vertical-align': 'top', 'border-right': '1px solid #dee2e6'}),
                                        html.Td(id='watsan-catchup-text', className='narrative-td', # Unique ID
                                              style={'vertical-align': 'top'})
                                    ])
                                ])
                            ], bordered=True, hover=True, responsive=True,
                            style={'margin-bottom': '0', 'border': '1px solid #dee2e6'})
                        ])
                    ], style={'height': '100%'})
                ])
            ], style={'align-items': 'stretch'})
        ])
    ])
])


# Indicator dropdown callback
@dash.callback(
    Output('watsan-indicator-dropdown', 'options'), # Unique ID
    Output('watsan-indicator-dropdown', 'value'), # Unique ID
    Input('watsan-outcome-dropdown', 'value'), # Unique ID
    prevent_initial_call=True
)
def update_indicators(selected_outcome):
    if not selected_outcome or df.empty:
        return [], None
    
    # Get indicators for the selected outcome
    filtered_df = df[df['Outcome'] == selected_outcome]
    indicators = filtered_df['Indicators'].unique().tolist()
    
    # Filter out None/null indicators
    indicators = [i for i in indicators if i and str(i).strip()]
    
    options = [{'label': i, 'value': i} for i in indicators]
    return options, indicators[0] if indicators else None

# Callback to update indicator-specific components
@dash.callback(
    Output('watsan-baseline-value', 'children'), # Unique ID
    Output('watsan-target-2024-value', 'children'), # Unique ID
    Output('watsan-target-midterm-value', 'children'), # Unique ID
    Output('watsan-current-value', 'children'), # Unique ID
    Output('watsan-progress-2024', 'children'), # Unique ID
    Output('watsan-progress-midterm', 'children'), # Unique ID
    Output('watsan-drivers-text', 'children'), # Unique ID
    Output('watsan-challenges-text', 'children'), # Unique ID
    Output('watsan-catchup-text', 'children'), # Unique ID
    Input('watsan-indicator-dropdown', 'value') # Unique ID
)
def update_indicator_data(selected_indicator):
    if not selected_indicator or df.empty:
        raise PreventUpdate
    
    # Get the row for the selected indicator
    indicator_rows = df[df['Indicators'] == selected_indicator]
    if indicator_rows.empty:
        raise PreventUpdate
        
    indicator_row = indicator_rows.iloc[0]
    
    # Get unit for display
    unit = indicator_row.get('Units', '')
    
    # Format values with units - handle potential NaN values
    def format_value(value, unit):
        if pd.isna(value):
            return "N/A"
        try:
            return f"{float(value):.1f} {unit}" if unit else f"{float(value):.1f}"
        except (ValueError, TypeError):
            return f"{value} {unit}" if unit else str(value)
    
    baseline_display = format_value(indicator_row.get('Baseline'), unit)
    target_2024_display = format_value(indicator_row.get('2024/25 Target'), unit)
    target_midterm_display = format_value(indicator_row.get('2026/27 Target'), unit)
    current_display = format_value(indicator_row.get('Current progress'), unit)
    
    # Create progress bars - handle potential NaN values
    def safe_percentage(value):
        if pd.isna(value):
            return 0
        try:
            value = float(value)
            return value * 100  # Multiply only if <= 1
        except (ValueError, TypeError):
            return 0
    
    progress_2024_value = safe_percentage(indicator_row.get('Percentage Progress based on 2024/25 Target'))
    progress_midterm_value = safe_percentage(indicator_row.get('Percentage Progress based on 2026/27 Target'))
    
    progress_2024_bar = create_progress_bar(
        progress_2024_value,
        "FY2024/25 PERCENTAGE PROGRESS"
    )
    
    progress_midterm_bar = create_progress_bar(
        progress_midterm_value,
        "NST2 MIDTERM PERCENTAGE PROGRESS"
    )
    
    # Handle narrative text fields
    drivers_text = indicator_row.get('Major drivers of performance', 'No data available')
    challenges_text = indicator_row.get('Challenges', 'No data available')
    catchup_text = indicator_row.get('Catch up Plans', 'No data available')
    
    return (
        baseline_display,
        target_2024_display,
        target_midterm_display,
        current_display,
        progress_2024_bar,
        progress_midterm_bar,
        drivers_text,
        challenges_text,
        catchup_text
    )