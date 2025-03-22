#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output

# Sample data (replace with your real data later)
dates = pd.date_range(start='2025-03-01', end='2025-03-12', freq='H')
zones = ['Adults B1', 'Pediatrics', 'Protocol', 'UCC']
acuities = ['ESI1', 'ESI2', 'ESI3', 'ESI4', 'ESI5']
dispositions = ['Admitted', 'Discharged']
np.random.seed(42)
sample_data = pd.DataFrame({
    'date': np.tile(dates, len(zones)),
    'zone': np.repeat(zones, len(dates)),
    'acuity': np.random.choice(acuities, len(dates) * len(zones)),
    'disposition': np.random.choice(dispositions, len(dates) * len(zones)),
    'length_of_stay': np.random.normal(180, 60, len(dates) * len(zones)),  # in minutes
    'door_to_doc': np.random.normal(20, 10, len(dates) * len(zones)),
    'doc_to_dispo': np.random.normal(150, 50, len(dates) * len(zones)),
    'boarding_time': np.random.normal(60, 30, len(dates) * len(zones)) * (np.random.choice([0, 1], len(dates) * len(zones), p=[0.5, 0.5])),  # 0 for discharged
    'lwbs': np.random.choice([0, 1], len(dates) * len(zones), p=[0.9, 0.1]),  # 0 = stayed, 1 = left
    'revisit_72h': np.random.choice([0, 1], len(dates) * len(zones), p=[0.95, 0.05])  # 0 = no revisit
})

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "KFSHRC-R Emergency Department Dashboard"

# Function to create KPI boxes
def create_kpi_boxes(total_visits, avg_los, avg_door_to_doc, avg_doc_to_dispo, avg_boarding_time, lwbs_rate, revisit_rate):
    return html.Div(
        style={
            'display': 'flex', 
            'flexWrap': 'wrap', 
            'justifyContent': 'space-between', 
            'gap': '15px', 
            'marginBottom': '20px',
            'maxWidth': '1200px', 
            'marginLeft': 'auto', 
            'marginRight': 'auto'
        },
        children=[
            html.Div([
                html.H3("Total Visits", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{total_visits}", style={'color': '#3498db', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'}),
            html.Div([
                html.H3("Avg LOS", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{avg_los:.1f} min", style={'color': '#3498db', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'}),
            html.Div([
                html.H3("Avg Door-to-Doc", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{avg_door_to_doc:.1f} min", style={'color': '#3498db', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'}),
            html.Div([
                html.H3("Avg Doc-to-Dispo", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{avg_doc_to_dispo:.1f} min", style={'color': '#3498db', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'}),
            html.Div([
                html.H3("Avg Boarding Time", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{avg_boarding_time:.1f} min" if not pd.isna(avg_boarding_time) else "N/A", style={'color': '#3498db', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'}),
            html.Div([
                html.H3("LWBS Rate", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{lwbs_rate:.1f}%", style={'color': '#e74c3c', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'}),
            html.Div([
                html.H3("72h Revisit Rate", style={'color': '#7f8c8d', 'fontWeight': 'bold', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.H2(f"{revisit_rate:.1f}%", style={'color': '#e74c3c', 'margin': '0'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1 1 150px', 'minWidth': '150px', 'textAlign': 'center'})
        ]
    )

# Layout with Tabs
app.layout = html.Div(
    style={'backgroundColor': '#f5f6f5', 'fontFamily': 'Arial', 'padding': '20px'},
    children=[
        html.H1("KFSHRC-R Emergency Department Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),

        # Date Picker
        html.Div([
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=sample_data['date'].min(),
                max_date_allowed=sample_data['date'].max(),
                initial_visible_month=sample_data['date'].max(),
                start_date=sample_data['date'].min(),
                end_date=sample_data['date'].max()
            )
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),

        # Tabs
        dcc.Tabs(id='tabs', value='overall', children=[
            # Tab 1: Overall ED
            dcc.Tab(label='Overall ED', value='overall', children=[
                html.Div(id='overall-kpis'),
                dash_table.DataTable(
                    id='data-table',
                    columns=[
                        {'name': 'Date', 'id': 'date'},
                        {'name': 'Zone', 'id': 'zone'},
                        {'name': 'Acuity', 'id': 'acuity'},
                        {'name': 'Disposition', 'id': 'disposition'},
                        {'name': 'LOS (min)', 'id': 'length_of_stay'},
                        {'name': 'Door-to-Doc (min)', 'id': 'door_to_doc'},
                        {'name': 'Doc-to-Dispo (min)', 'id': 'doc_to_dispo'},
                        {'name': 'Boarding Time (min)', 'id': 'boarding_time'},
                        {'name': 'LWBS', 'id': 'lwbs'},
                        {'name': '72h Revisit', 'id': 'revisit_72h'}
                    ],
                    style_table={'overflowX': 'auto'},
                    virtualization=True,
                    page_size=10
                )
            ]),

            # Tab 2: Zones
            dcc.Tab(label='Zones', value='zones', children=[
                html.Div([
                    dcc.Dropdown(
                        id='zone-dropdown',
                        options=[{'label': zone, 'value': zone} for zone in zones],
                        value=zones[0],  # Default to first zone
                        style={'width': '50%', 'margin': '0 auto 20px auto'}
                    ),
                    html.Div(id='zone-kpis'),
                    dcc.Graph(id='zone-graph')
                ], style={'maxWidth': '1200px', 'marginLeft': 'auto', 'marginRight': 'auto'})
            ]),

            # Tab 3: Acuity
            dcc.Tab(label='Acuity', value='acuity', children=[
                html.Div([
                    dcc.Dropdown(
                        id='acuity-dropdown',
                        options=[{'label': acuity, 'value': acuity} for acuity in acuities],
                        value=acuities[0],  # Default to first acuity
                        style={'width': '50%', 'margin': '0 auto 20px auto'}
                    ),
                    html.Div(id='acuity-kpis'),
                    dcc.Graph(id='acuity-graph')
                ], style={'maxWidth': '1200px', 'marginLeft': 'auto', 'marginRight': 'auto'})
            ]),

            # Tab 4: Disposition
            dcc.Tab(label='Disposition', value='disposition', children=[
                html.Div([
                    dcc.Dropdown(
                        id='disposition-dropdown',
                        options=[{'label': disp, 'value': disp} for disp in dispositions],
                        value=dispositions[0],  # Default to first disposition
                        style={'width': '50%', 'margin': '0 auto 20px auto'}
                    ),
                    html.Div(id='disposition-kpis'),
                    dcc.Graph(id='disposition-graph')
                ], style={'maxWidth': '1200px', 'marginLeft': 'auto', 'marginRight': 'auto'})
            ]),

            # Tab 5: Demand Prediction
            dcc.Tab(label='Demand Prediction', value='demand', children=[
                html.Div([
                    html.H2("Demand Prediction (Hourly)", style={'textAlign': 'center', 'color': '#2c3e50'}),
                    dcc.Graph(id='demand-prediction')
                ], style={'maxWidth': '1200px', 'marginLeft': 'auto', 'marginRight': 'auto'})
            ])
        ])
    ]
)

# Callback to update all components
@app.callback(
    [Output('overall-kpis', 'children'),
     Output('zone-kpis', 'children'),
     Output('zone-graph', 'figure'),
     Output('acuity-kpis', 'children'),
     Output('acuity-graph', 'figure'),
     Output('disposition-kpis', 'children'),
     Output('disposition-graph', 'figure'),
     Output('demand-prediction', 'figure'),
     Output('data-table', 'data')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('zone-dropdown', 'value'),
     Input('acuity-dropdown', 'value'),
     Input('disposition-dropdown', 'value')]
)
def update_dashboard(start_date, end_date, selected_zone, selected_acuity, selected_disposition):
    # Filter data by date range
    filtered_data = sample_data[
        (sample_data['date'] >= start_date) & 
        (sample_data['date'] <= end_date)
    ]

    # Overall ED KPIs
    overall_visits = len(filtered_data)
    overall_los = filtered_data['length_of_stay'].mean()
    overall_door_to_doc = filtered_data['door_to_doc'].mean()
    overall_doc_to_dispo = filtered_data['doc_to_dispo'].mean()
    overall_boarding_time = filtered_data[filtered_data['boarding_time'] > 0]['boarding_time'].mean()
    overall_lwbs_rate = filtered_data['lwbs'].mean() * 100
    overall_revisit_rate = filtered_data['revisit_72h'].mean() * 100
    overall_kpis = create_kpi_boxes(overall_visits, overall_los, overall_door_to_doc, overall_doc_to_dispo, 
                                    overall_boarding_time, overall_lwbs_rate, overall_revisit_rate)

    # Zone KPIs and Graph
    zone_data = filtered_data[filtered_data['zone'] == selected_zone]
    zone_visits = len(zone_data)
    zone_los = zone_data['length_of_stay'].mean()
    zone_door_to_doc = zone_data['door_to_doc'].mean()
    zone_doc_to_dispo = zone_data['doc_to_dispo'].mean()
    zone_boarding_time = zone_data[zone_data['boarding_time'] > 0]['boarding_time'].mean()
    zone_lwbs_rate = zone_data['lwbs'].mean() * 100
    zone_revisit_rate = zone_data['revisit_72h'].mean() * 100
    zone_kpis = create_kpi_boxes(zone_visits, zone_los, zone_door_to_doc, zone_doc_to_dispo, 
                                 zone_boarding_time, zone_lwbs_rate, zone_revisit_rate)
    zone_stats = filtered_data.groupby('zone').agg({
        'length_of_stay': 'mean',
        'door_to_doc': 'mean',
        'doc_to_dispo': 'mean',
        'boarding_time': lambda x: x[x > 0].mean(),
        'lwbs': 'mean',
        'revisit_72h': 'mean'
    }).reset_index()
    zone_fig = go.Figure(data=[
        go.Bar(x=zone_stats['zone'], y=zone_stats['length_of_stay'], name='Avg LOS', marker_color='#3498db'),
        go.Bar(x=zone_stats['zone'], y=zone_stats['door_to_doc'], name='Avg Door-to-Doc', marker_color='#2ecc71'),
        go.Bar(x=zone_stats['zone'], y=zone_stats['doc_to_dispo'], name='Avg Doc-to-Dispo', marker_color='#ffce56'),
        go.Bar(x=zone_stats['zone'], y=zone_stats['boarding_time'], name='Avg Boarding Time', marker_color='#9966ff')
    ]).update_layout(
        title='KPIs Across Zones', title_x=0.5, template='plotly_white', yaxis_title="Minutes", 
        barmode='group', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    # Acuity KPIs and Graph
    acuity_data = filtered_data[filtered_data['acuity'] == selected_acuity]
    acuity_visits = len(acuity_data)
    acuity_los = acuity_data['length_of_stay'].mean()
    acuity_door_to_doc = acuity_data['door_to_doc'].mean()
    acuity_doc_to_dispo = acuity_data['doc_to_dispo'].mean()
    acuity_boarding_time = acuity_data[acuity_data['boarding_time'] > 0]['boarding_time'].mean()
    acuity_lwbs_rate = acuity_data['lwbs'].mean() * 100
    acuity_revisit_rate = acuity_data['revisit_72h'].mean() * 100
    acuity_kpis = create_kpi_boxes(acuity_visits, acuity_los, acuity_door_to_doc, acuity_doc_to_dispo, 
                                   acuity_boarding_time, acuity_lwbs_rate, acuity_revisit_rate)
    acuity_stats = filtered_data.groupby('acuity').agg({
        'length_of_stay': 'mean',
        'door_to_doc': 'mean',
        'doc_to_dispo': 'mean',
        'boarding_time': lambda x: x[x > 0].mean(),
        'lwbs': 'mean',
        'revisit_72h': 'mean'
    }).reset_index()
    acuity_fig = go.Figure(data=[
        go.Bar(x=acuity_stats['acuity'], y=acuity_stats['length_of_stay'], name='Avg LOS', marker_color='#3498db'),
        go.Bar(x=acuity_stats['acuity'], y=acuity_stats['door_to_doc'], name='Avg Door-to-Doc', marker_color='#2ecc71'),
        go.Bar(x=acuity_stats['acuity'], y=acuity_stats['doc_to_dispo'], name='Avg Doc-to-Dispo', marker_color='#ffce56'),
        go.Bar(x=acuity_stats['acuity'], y=acuity_stats['boarding_time'], name='Avg Boarding Time', marker_color='#9966ff')
    ]).update_layout(
        title='KPIs Across Acuity Levels', title_x=0.5, template='plotly_white', yaxis_title="Minutes", 
        barmode='group', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    # Disposition KPIs and Graph
    disposition_data = filtered_data[filtered_data['disposition'] == selected_disposition]
    disposition_visits = len(disposition_data)
    disposition_los = disposition_data['length_of_stay'].mean()
    disposition_door_to_doc = disposition_data['door_to_doc'].mean()
    disposition_doc_to_dispo = disposition_data['doc_to_dispo'].mean()
    disposition_boarding_time = disposition_data[disposition_data['boarding_time'] > 0]['boarding_time'].mean()
    disposition_lwbs_rate = disposition_data['lwbs'].mean() * 100
    disposition_revisit_rate = disposition_data['revisit_72h'].mean() * 100
    disposition_kpis = create_kpi_boxes(disposition_visits, disposition_los, disposition_door_to_doc, disposition_doc_to_dispo, 
                                        disposition_boarding_time, disposition_lwbs_rate, disposition_revisit_rate)
    disposition_stats = filtered_data.groupby('disposition').agg({
        'length_of_stay': 'mean',
        'door_to_doc': 'mean',
        'doc_to_dispo': 'mean',
        'boarding_time': lambda x: x[x > 0].mean(),
        'lwbs': 'mean',
        'revisit_72h': 'mean'
    }).reset_index()
    disposition_fig = go.Figure(data=[
        go.Bar(x=disposition_stats['disposition'], y=disposition_stats['length_of_stay'], name='Avg LOS', marker_color='#3498db'),
        go.Bar(x=disposition_stats['disposition'], y=disposition_stats['door_to_doc'], name='Avg Door-to-Doc', marker_color='#2ecc71'),
        go.Bar(x=disposition_stats['disposition'], y=disposition_stats['doc_to_dispo'], name='Avg Doc-to-Dispo', marker_color='#ffce56'),
        go.Bar(x=disposition_stats['disposition'], y=disposition_stats['boarding_time'], name='Avg Boarding Time', marker_color='#9966ff')
    ]).update_layout(
        title='KPIs Across Dispositions', title_x=0.5, template='plotly_white', yaxis_title="Minutes", 
        barmode='group', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    # Demand Prediction (Separate Tab)
    hourly_visits = filtered_data.groupby(pd.Grouper(key='date', freq='H')).size().reset_index(name='count')
    demand_fig = px.line(hourly_visits, x='date', y='count', title='Hourly ED Visits', 
                         template='plotly_white', line_shape='linear', color_discrete_sequence=['#3498db'])\
        .update_layout(yaxis_title="Number of Visits", xaxis_title="", plot_bgcolor='rgba(0,0,0,0)')

    # Table Data (Overall ED only)
    table_data = filtered_data.to_dict('records')

    return (overall_kpis, zone_kpis, zone_fig, acuity_kpis, acuity_fig, disposition_kpis, disposition_fig, demand_fig, table_data)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)  # Using port 8051 to avoid conflicts


# In[ ]:




