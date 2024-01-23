from dash import Dash, dcc, html, Input, Output, State, no_update, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from dash import Dash, dcc, html, Input, Output
import dash_design_kit as ddk
import plotly.express as px

import json
import constants
import datetime

app = Dash(__name__)
server = app.server  # expose server variable for Procfile

constants.redis_instance.hset("realtime", 'data-cache', '')

app.layout = ddk.App([
    dcc.Interval(
        id='ticktock',
        interval=1000, # in milliseconds
        n_intervals=0
    ),
    dcc.Store(id='lasttime'),
    ddk.Header([
        ddk.Title('Real-time Data from ERDDAP as fast as we can.'),
    ]),
    ddk.Row(children=[
        ddk.Card(children=[
            ddk.CardHeader(id='header'),
            ddk.Graph(id='fakey', style={'height':300}),
        ]),
    ]),
    html.Div(id='kick', style={'display':'none'})
])


@app.callback(
    [
        Output('fakey', 'figure'),
        Output('header', 'title'),
        Output('lasttime', 'data')
    ],
    [
        Input('kick', 'n_clicks')
    ],
)
def kick_off(click):   
    try:
        pdf = pd.read_csv('https://datalocal.pmel.noaa.gov/erddap/tabledap/fake_push_test.csv?time%2Cfake&platform_id=%22spaceship005%22&time>2024-01-02', skiprows=[1])
        title = 'ERDDAP: Initial load -- data set has ' + str(pdf.shape[0]) + ' ending at '
    except:
        print('no data found in ERDDAP during kick_off')
        pdf = pd.DataFrame(np.nan, index=[0, 1, 2, 3], columns=['time', 'fake'])
        pdf['time'] = pd.to_datetime(pdf['time'])
        print(pdf)
        figure = px.line(pdf, 'time', 'fake')
        print(figure)
        return figure, 'No data yet for this platform', ''  
    timemax = pdf['time'].max()
    print('returning last time of ' + timemax, timemax,  'with figure of length ', pdf['time'].shape[0])
    print(pdf)
    figure = px.line(pdf, 'time', 'fake')
    print(figure)
    return [figure, title + timemax, timemax]



@app.callback(
    [
       Output('fakey', 'extendData'),
       Output('header', 'title', allow_duplicate=True),
       Output('lasttime', 'data', allow_duplicate=True)
    ],
    [
        Input('ticktock', 'n_intervals')
    ],
    [
        State('lasttime', 'data')
    ], prevent_initial_call=True
)
def plot(tick, lasttime):
    if lasttime is not None and len(lasttime) > 0:
        print('updating data from lasttime=', lasttime, ' forward.')
        try:
            url = 'https://datalocal.pmel.noaa.gov/erddap/tabledap/fake_push_test.csv?time%2Cfake&platform_id=%22spaceship005%22&time>' + lasttime
            ndf = pd.read_csv(url, skiprows=[1])
            print('new data size=',ndf.shape[0])
            title = 'Added ' + str(ndf.shape[0]) + ' new points ending at ' + ndf['time'].max()
            print(ndf['time'].tolist())
            return [dict(x=[ndf['time'].tolist()], y=[ndf['fake'].tolist()]), title, ndf['time'].max()]
        except:
            return [no_update, 'No new data found', no_update]
    else:
        try:
            pdf = pd.read_csv('https://datalocal.pmel.noaa.gov/erddap/tabledap/fake_push_test.csv?time%2Cfake&platform_id=%22spaceship005%22&time>2024-01-02', skiprows=[1])
            timemax = pdf['time'].max()
            title = 'New data has started to arrive ' + str(pdf.shape[0]) + ' ending at ' + timemax
            print('returning last time of ', timemax,  'with figure of length ', pdf['time'].shape[0])
            return [dict(x=[pdf['time'].tolist()], y=[pdf['fake'].tolist()]), title, timemax]
        except:
            return [no_update, no_update, no_update]


if __name__ == '__main__':
    app.run_server(debug=True)

