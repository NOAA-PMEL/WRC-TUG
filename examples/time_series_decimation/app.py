from dash import Dash, dcc, html, Input, Output, callback_context, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib
from sdig.erddap.info import Info


def get_blank(message):
    blank_graph = go.Figure(go.Scatter(x=[0, 1], y=[0, 1], showlegend=False))
    blank_graph.add_trace(go.Scatter(x=[0, 1], y=[0, 1], showlegend=False))
    blank_graph.update_traces(visible=False)
    blank_graph.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        title=message,
        plot_bgcolor='rgba(1.0, 1.0, 1.0 ,1.0)',
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 14
                }
            },
        ]
    )
    return blank_graph


app = Dash(__name__)
server = app.server  # expose server variable for Procfile

info1 = Info('https://data.pmel.noaa.gov/pmel/erddap/tabledap/all_swfsc_2022')
info2 = Info('https://data.pmel.noaa.gov/pmel/erddap/tabledap/all_swfsc_2023')

vars1, long1, units1, stdn1, types1 = info1.get_variables()
vars2, long2, units2, stdn2, types2 = info2.get_variables()

for t in types1:
    if types1[t] == 'String' and t != 'time':
        types1[t] = 'str'
del types1['time']

for t in types2:
    if types2[t] == 'String' and t != 'time':
        types2[t] = 'str'
del types2['time']
    
ob = urllib.parse.quote('&orderByClosest("trajectory, time/3days")', safe='&()=:/')

df1 = pd.read_csv(info1.url + '.csv?' + ','.join(vars1) + ob, skiprows=[1], dtype=types1, parse_dates=True)
df2 = pd.read_csv(info2.url + '.csv?' + ','.join(vars2) + ob, skiprows=[1], dtype=types2, parse_dates=True)

trace_figure = px.scatter_geo(df1, lat='latitude', lon='longitude', color='trajectory', fitbounds='locations', custom_data='trajectory')

app.layout = html.Div([
    html.Div(style={'height': '195px'}, children=[
        html.H1('Simple Dash App'),
        html.H2('Uses the callback_context to decide how to update the timeseries plot.'),
        html.H3('The callback reacts to either click on a platform to plot the time series, or a menu change to reset the graph.')
    ]),
    dcc.Dropdown(
        id='mission-dropdown',
        style={'width': '400px'},
        options=[
            {'label': 'Saildrone 2022 NOAA SWFSC NRT', 'value': 'fish1'},
            {'label': 'Saildrone 2023 NOAA SWFSC NRT', 'value': 'fish2'},
        ], value='fish1'
    ),
    html.Div(style={'display': 'flex'}, children=[
        html.Div(style={"width": "600px"}, children=[dcc.Graph(id='map', figure=trace_figure)]),
        html.Div(style={"flex-grow": "1", "float": "right"}, children=[dcc.Graph(id='timeseries', figure=get_blank('Click a dot on the map.'))]),
    ])
    
    
])


@app.callback(
    [
        Output('map', 'figure')
    ],
    [
        Input('mission-dropdown', 'value')
    ], 
    prevent_initial_call=True
)
def plot_map(mission):
    if mission == 'fish1':
        return [px.scatter_geo(df1, lat='latitude', lon='longitude', color='trajectory', fitbounds='locations', custom_data='trajectory')]
    elif mission == 'fish2':
        return [px.scatter_geo(df2, lat='latitude', lon='longitude', color='trajectory', fitbounds='locations', custom_data='trajectory')]
    else:
        return no_update


@app.callback(
    [
        Output('timeseries', 'figure')
    ],
    [
        Input('mission-dropdown', 'value'),
        Input('map', 'clickData')
    ], 
    prevent_initial_call=True
)
def plot_timeseries(mission, click):
    if callback_context.triggered_id == 'mission-dropdown':
        return [get_blank('Click a dot on the map.')]
    elif callback_context.triggered_id == 'map':
        if 'points' in click:
            first_p = click['points'][0]
            click_choice = first_p['customdata'][0]
            color_num = first_p['curveNumber']
        if mission == 'fish1':
            df = df1.loc[df1['trajectory']==click_choice]
            fig = px.line(df, x='time', y='TEMP_AIR_MEAN' , color='trajectory')
            fig.update_traces(line_color=px.colors.qualitative.Plotly[color_num])
            return [fig]
        elif mission == 'fish2':
            df = df2.loc[df2['trajectory']==click_choice]
            fig = px.line(df, x='time', y='TEMP_AIR_MEAN' , color='trajectory')
            fig.update_traces(line_color=px.colors.qualitative.Plotly[color_num])
            return[fig]
        else:
            return no_update
    else:
        return no_update


if __name__ == '__main__':
    app.run_server(debug=True)