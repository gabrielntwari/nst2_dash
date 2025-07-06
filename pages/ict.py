# pages/ict.py

import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd

# IMPORTANT: Register this file as a page in the main Dash application.
# The 'path' defines the URL for this page (e.g., http://localhost:8050/ict)
# The 'name' is what will be displayed in your sidebar navigation.
dash.register_page(__name__, path='/ict', name='ICT Dashboard')

# --- Data Loading and Processing (Keep as is, ensure 'ICT.xlsx' is accessible) ---
try:
    df = pd.read_excel('ICT.xlsx')
    df['Units'] = df['Units'].str.replace('Percent', '%', regex=False)
    df = df.dropna(subset=['Outcome'])
    df['Outcome'] = df['Outcome'].astype(str)
    df = df[df['Outcome'] != '']
except FileNotFoundError:
    print("Error: ICT.xlsx file not found. Using empty DataFrame.")
    df = pd.DataFrame()

outcomes = [o for o in df['Outcome'].unique().tolist() if o and str(o)]
indicators_by_outcome = df.groupby('Outcome')['Indicators'].apply(list).to_dict()

status_2024_counts = df['Status based on 2024/25 Target'].value_counts().to_dict()
status_midterm_counts = df['Status based on NST2 Midterm target'].value_counts().to_dict()

all_statuses = ['GOOD', 'SATISFACTORY', 'COMPLETED', 'LOW']
status_2024_counts = {status: status_2024_counts.get(status, 0) for status in all_statuses}
status_midterm_counts = {status: status_midterm_counts.get(status, 0) for status in all_statuses}

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
        marker_colors=['','#28a745', '#ffc107', 'red'] ,
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
        html.Li(["Rwanda views ICT as a key enabler of national development, with the Smart Rwanda Master Plan guiding digital transformation across sectors like education, health, agriculture, and governance"],
        className="summary-point")
    )
    
    summary_points.append(
        html.Li(["The country has achieved",
            html.Span(f"75%", className="highlight-percent"),
            " 4G LTE coverage and",
            html.Span(f"8.6 million  ", className="highlight-number"),
            "subscribers with over",
            html.Span(f"70% ", className="highlight-percent"),
            "of priority government services available online or via mobile platforms.",
            html.Span(" ↗", className="trend-up")
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["Basic digital literacy among citizens stands at",
            html.Span(f"74.7%", className="highlight-percent"),
            ", internet access in schools is at",
            html.Span(f"61.8%", className="highlight-percent"),
            ", while smartphone ownership remains low at",
            html.Span(f"34%", className="highlight-percent"),
            html.Span(" ✓", className="check-badge")
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["Limited connectivity in rural areas due to poor electrification and high broadband and hosting costs hinder accessibility and affordability.",
            html.Span(" ↓", className="check-badge")
        ], className="summary-point")
    )
    
    summary_points.append(
        html.Li(["The sector suffers from outdated cybersecurity infrastructure and a shortage of skilled professionals due to limited specialized training.",
            html.Span(" ↓", className="trend-up")
        ], className="summary-point")
    )
    
    return summary_points

# --- Layout of the ICT Dashboard Page ---
# This variable MUST be named 'layout' for Dash to find it.
layout = html.Div([
    # No dcc.Location here, it's handled by the main app.
    # No html.Div(id='page-content') wrapper needed here.
    
    html.Div(className='main-content-wrapper', children=[ # Re-using a class from your CSS
        
        # Removed Header Section
        # html.Div(className='dashboard-header', children=[
        #     html.H1("", className='dashboard-title'),
        #     html.Div(className='dashboard-subtitle', children="")
        # ]),
        
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
                    id='ict-outcome-dropdown', # Unique ID
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
                    id='ict-indicator-dropdown', # Unique ID
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
                            html.Div(id='ict-baseline-value', className="indicator-value", # Unique ID
                                     style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6),
                    
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("2024/25 Target", className='indicator-header',
                                     style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            html.Div(id='ict-target-2024-value', className="indicator-value", # Unique ID
                                     style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6)
                ], style={'margin-bottom': '15px'}),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("2026/27 Target", className='indicator-header',
                                     style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            html.Div(id='ict-target-midterm-value', className="indicator-value", # Unique ID
                                     style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6),
                    
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Current Progress", className='indicator-header',
                                     style={'background-color': '#f8f9fa', 'font-weight': 'bold'}),
                        dbc.CardBody([
                            html.Div(id='ict-current-value', className="indicator-value", # Unique ID
                                     style={'font-size': '1.5rem', 'font-weight': 'bold', 'text-align': 'center'})
                        ])
                    ], className='indicator-card'), width=6)
                ], style={'margin-bottom': '15px'}),
                # Progress Bars
                dbc.Row([
                    dbc.Col(html.Div(id='ict-progress-2024'), width=6), # Unique ID
                    dbc.Col(html.Div(id='ict-progress-midterm'), width=6) # Unique ID
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
                                    html.Td(id='ict-drivers-text', className='narrative-td', # Unique ID
                                            style={'vertical-align': 'top', 'border-right': '1px solid #dee2e6'}),
                                    html.Td(id='ict-challenges-text', className='narrative-td', # Unique ID
                                            style={'vertical-align': 'top', 'border-right': '1px solid #dee2e6'}),
                                    html.Td(id='ict-catchup-text', className='narrative-td', # Unique ID
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

# --- Callbacks for ICT Dashboard (Keep as is, but add allow_duplicate=True) ---

# Indicator dropdown callback (Keep as is)
@dash.callback( # Use dash.callback instead of app.callback in page files
    Output('ict-indicator-dropdown', 'options'), # Updated ID
    Output('ict-indicator-dropdown', 'value'), # Updated ID
    Input('ict-outcome-dropdown', 'value'), # Updated ID
    prevent_initial_call=True # No longer needs 'initial_duplicate' as IDs are unique
)
def update_indicators(selected_outcome):
    if not selected_outcome or df.empty:
        raise PreventUpdate
    
    filtered_df = df[df['Outcome'] == selected_outcome]
    indicators = filtered_df['Indicators'].unique().tolist()
    indicators = [i for i in indicators if i and str(i).strip()]
    
    options = [{'label': i, 'value': i} for i in indicators]
    return options, indicators[0] if indicators else None

# Callback to update indicator-specific components (Keep as is)
@dash.callback( # Use dash.callback instead of app.callback in page files
    Output('ict-baseline-value', 'children'), # Updated ID
    Output('ict-target-2024-value', 'children'), # Updated ID
    Output('ict-target-midterm-value', 'children'), # Updated ID
    Output('ict-current-value', 'children'), # Updated ID
    Output('ict-progress-2024', 'children'), # Updated ID
    Output('ict-progress-midterm', 'children'), # Updated ID
    Output('ict-drivers-text', 'children'), # Updated ID
    Output('ict-challenges-text', 'children'), # Updated ID
    Output('ict-catchup-text', 'children'), # Updated ID
    Input('ict-indicator-dropdown', 'value'), # Updated ID
    prevent_initial_call=True # No longer needs 'initial_duplicate' as IDs are unique
)
def update_indicator_data(selected_indicator):
    if not selected_indicator or df.empty:
        raise PreventUpdate
    
    indicator_rows = df[df['Indicators'] == selected_indicator]
    if indicator_rows.empty:
        raise PreventUpdate
        
    indicator_row = indicator_rows.iloc[0]
    
    unit = indicator_row.get('Units', '')
    
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
    
    def safe_percentage(value):
        if pd.isna(value):
            return 0
        try:
            value = float(value)
            return value * 100 
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
