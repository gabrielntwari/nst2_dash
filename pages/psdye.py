# pages/psdye.py

import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd

# IMPORTANT: Register this file as a page in the main Dash application.
# The 'path' defines the URL for this page (e.g., http://localhost:8050/psdye)
# The 'name' is what will be displayed in your sidebar navigation.
dash.register_page(__name__, path='/psdye', name='PSDYE Dashboard')

# --- Data Loading and Processing (Keep as is, ensure 'psdye.xlsx' is accessible) ---
df = pd.read_excel('psdye.xlsx')
df['Units'] = df['Units'].str.replace('Percent', '%', regex=False)

outcomes = df['Outcome'].unique().tolist()
indicators_by_outcome = df.groupby('Outcome')['Indicators'].apply(list).to_dict()

status_2024_counts = df['Status based on 2024/25 Target'].value_counts().to_dict()
status_midterm_counts = df['Status based on NST2 Midterm target'].value_counts().to_dict()

for status in ['GOOD', 'SATISFACTORY', 'COMPLETED']:
    if status not in status_2024_counts:
        status_2024_counts[status] = 0
    if status not in status_midterm_counts:
        status_midterm_counts[status] = 0

total_outcomes = len(outcomes)
total_indicators = len(df)
avg_progress_2024 = df['Percentage Progress based on 2024/25 Target'].mean()
avg_progress_midterm = df['Percentage Progress based on 2026/27 Target'].mean()

# --- Helper Functions (Keep as is) ---
def pie_chart(data, title):
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        hole=0.3,
        marker_colors=['ligtblue', 'green', 'yellow'], # Note: Your ICT.py had 'red' first, consider consistency
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
            html.Li([
                html.Span(f"1.37 million", className="highlight-number"),
                " productive and decent jobs created achieving",
                html.Span(f"92%", className="highlight-percent"),
                " of NST1 target."
            ], className="summary-point")
        )
    
    summary_points.append(
            html.Li(["Export revenues increased from",
                html.Span(f"USD 1.9 billion", className="highlight-number"),
                "in 2017 to",
                html.Span(f"USD 3.5 billion ", className="highlight-number"),
                "in 2023, driven by growth in minerals, manufacturing, and services.",
                html.Span(" ↗", className="trend-up")
            ], className="summary-point")
        )
    
    summary_points.append(
            html.Li(["The tourism sector generated",
                html.Span(f"USD 620 million", className="highlight-number"),
                "n 2023, with MICE tourism growing over",
                html.Span(f"40%", className="highlight-percent"),
                "year-on-year",
                html.Span(" ✓", className="check-badge")
            ], className="summary-point")
        )
    
    summary_points.append(
        html.Li(["The industrial sector expanded to",
            html.Span(f"22%", className="highlight-percent"),
            f" of GDP with continued support to MSMEs, which employ over",
            html.Span("2.6 million", className="highlight-number"),
            "people and contribute to ",
            html.Span(f"33%", className="highlight-percent"),
            "to GDP.",
            html.Span(" ✓", className="check-badge")
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["MSMEs, which make up over",
            html.Span(f"90%", className="highlight-percent"),
            " of all businesses, employed ",
            html.Span(f"2.6 million", className="highlight-number"),
            " people and contributed",
            html.Span(f"33%", className="highlight-percent"),
            " to GDP.",
            html.Span(" ↗", className="trend-up")
        ], className="summary-point")
    )
    
    return summary_points

# --- Layout of the PSDYE Dashboard Page ---
# This variable MUST be named 'layout' for Dash to find it.
layout = html.Div([
    # No dcc.Location here, it's handled by the main app.
    # No html.Div(id='page-content') wrapper needed here.
    
    html.Div(className='main-content-wrapper', children=[
        
        # 1. Header Section
       # html.Div(className='dashboard-header', children=[
           # html.H1("PSDYE SSP PROGRESS DASHBOARD", className='dashboard-title'),
           # html.Div(className='dashboard-subtitle', children="Comprehensive Overview of Sector Performance and Progress")
        #]),
        
        # 2. Top Row - Metrics and Summary
        dbc.Row(className='top-row', children=[
            # Metrics Cards
            dbc.Col(className='metrics-col', width=3, children=[
                dbc.Row([
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
                ], style={'height': '80%'})
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
                    id='psdye-outcome-dropdown', # Unique ID
                    options=[{'label': o, 'value': o} for o in outcomes],
                    value=outcomes[0] if outcomes else None,
                    className='outcome-dropdown',
                    style={'border-radius': '4px', 'border': '1px solid #ced4da'}
                )
            ]),
            dbc.Col(width=6, children=[
                html.Label("SELECT INDICATOR", className="dropdown-label",
                          style={'font-weight': 'bold', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='psdye-indicator-dropdown', # Unique ID
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
                            html.Div(id='psdye-baseline-value', className="indicator-value", # Unique ID
                                    style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6),
                    
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("2024/25 Target", className='indicator-header',
                                      style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            html.Div(id='psdye-target-2024-value', className="indicator-value", # Unique ID
                                    style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6)
                ], style={'margin-bottom': '15px'}),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("2026/27 Target", className='indicator-header',
                                      style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            html.Div(id='psdye-target-midterm-value', className="indicator-value", # Unique ID
                                    style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6),
                    
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Current Progress", className='indicator-header',
                                      style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            html.Div(id='psdye-current-value', className="indicator-value", # Unique ID
                                    style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6)
                ], style={'margin-bottom': '15px'}),
                # Progress Bars
                dbc.Row([
                    dbc.Col(html.Div(id='psdye-progress-2024'), width=6), # Unique ID
                    dbc.Col(html.Div(id='psdye-progress-midterm'), width=6) # Unique ID
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
                                    html.Td(id='psdye-drivers-text', className='narrative-td', # Unique ID
                                          style={'vertical-align': 'top', 'border-right': '1px solid #dee2e6'}),
                                    html.Td(id='psdye-challenges-text', className='narrative-td', # Unique ID
                                          style={'vertical-align': 'top', 'border-right': '1px solid #dee2e6'}),
                                    html.Td(id='psdye-catchup-text', className='narrative-td', # Unique ID
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

# --- Callbacks for PSDYE Dashboard (Unique IDs, prevent_initial_call=True) ---

# Indicator dropdown callback
@dash.callback( # Use dash.callback instead of app.callback in page files
    Output('psdye-indicator-dropdown', 'options'), # Updated ID
    Output('psdye-indicator-dropdown', 'value'), # Updated ID
    Input('psdye-outcome-dropdown', 'value'), # Updated ID
    prevent_initial_call=True # No longer needs 'initial_duplicate' as IDs are unique
)
def update_indicators(selected_outcome):
    if not selected_outcome:
        return [], None
    
    options = indicators_by_outcome.get(selected_outcome, [])
    return [{'label': i, 'value': i} for i in options], options[0] if options else None

# Callback to update indicator-specific components
@dash.callback( # Use dash.callback instead of app.callback in page files
    Output('psdye-baseline-value', 'children'), # Updated ID
    Output('psdye-target-2024-value', 'children'), # Updated ID
    Output('psdye-target-midterm-value', 'children'), # Updated ID
    Output('psdye-current-value', 'children'), # Updated ID
    Output('psdye-progress-2024', 'children'), # Updated ID
    Output('psdye-progress-midterm', 'children'), # Updated ID
    Output('psdye-drivers-text', 'children'), # Updated ID
    Output('psdye-challenges-text', 'children'), # Updated ID
    Output('psdye-catchup-text', 'children'), # Updated ID
    Input('psdye-indicator-dropdown', 'value'), # Updated ID
    prevent_initial_call=True # No longer needs 'initial_duplicate' as IDs are unique
)
def update_indicator_data(selected_indicator):
    if not selected_indicator:
        raise PreventUpdate
    
    indicator_row = df[df['Indicators'] == selected_indicator].iloc[0]
    
    unit = indicator_row['Units']
    
    baseline_display = f"{indicator_row['Baseline']:.1f} {unit}"
    target_2024_display = f"{indicator_row['2024/25 Target']:.1f} {unit}"
    target_midterm_display = f"{indicator_row['2026/27 Target']:.1f} {unit}"
    current_display = f"{indicator_row['Current progress']:.1f} {unit}"
    
    progress_2024_bar = create_progress_bar(
        indicator_row['Percentage Progress based on 2024/25 Target']*100,
        "FY2024/25 PERCENTAGE PROGRESS"
    )
    
    progress_midterm_bar = create_progress_bar(
        indicator_row['Percentage Progress based on 2026/27 Target']*100,
        "NST2 MIDTERM PERCENTAGE PROGRESS"
    )
    
    return (
        baseline_display,
        target_2024_display,
        target_midterm_display,
        current_display,
        progress_2024_bar,
        progress_midterm_bar,
        indicator_row['Major drivers of performance'],
        indicator_row['Challenges'],
        indicator_row['Catch up Plans']
    )
