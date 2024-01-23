from dash import Dash, dcc, html, Input, Output, State, no_update, callback_context
import dash_design_kit as ddk
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import redis
import os
import json
import constants
import datashader as ds
from sdig.erddap.info import Info

app = Dash(__name__)
server = app.server  # expose server variable for Procfile



data_url =  'http://hazy.pmel.noaa.gov:8140/erddap/tabledap/'

my_info = Info(data_url + 'sd1031_hurricane_2023')

variables, long_names, units, standard_names, dtypes = my_info.get_variables()
options = []
for var in variables:
    long_name = var
    if var in long_names:
        long_name = long_names[var]
    options.append({'label': long_name, 'value': var})


app.layout = ddk.App([
    dcc.Store(id='go'),
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png')),
        ddk.Title('Dash Enterprise Sample Application'),
    ]),
    ddk.Row(children=[
        ddk.ControlCard(width=.25, children=[
            ddk.ControlItem(children=[
                dcc.Dropdown(
                    id='title-dropdown',
                    options=options,
                    value='TEMP_AIR_MEAN'
                ),
            ]),
            ddk.ControlItem(children=[
                dcc.Dropdown(
                    id='drone-dropdown',
                    options=[
                        {'label': '1031', 'value':'sd1031_hurricane_2023'},
                        {'label': '1036', 'value':'sd1036_hurricane_2023'},
                        {'label': '1040', 'value':'sd1040_hurricane_2023'},
                        {'label': '1041', 'value':'sd1041_hurricane_2023'},
                        {'label': '1042', 'value':'sd1042_hurricane_2023'},
                        {'label': '1045', 'value':'sd1045_hurricane_2023'},
                        {'label': '1057', 'value':'sd1057_hurricane_2023'},
                        {'label': '1064', 'value':'sd1064_hurricane_2023'},
                        {'label': '1065', 'value':'sd1065_hurricane_2023'},
                        {'label': '1068', 'value':'sd1068_hurricane_2023'},
                        {'label': '1069', 'value':'sd1069_hurricane_2023'},
                        {'label': '1083', 'value':'sd1083_hurricane_2023'},
                    ],
                    value='sd1031_hurricane_2023'
                )
            ]),
        ]),
        ddk.ControlCard(width=.25, children=[
            ddk.ControlItem(
                html.Button(id='reset', children=['Reset Plots'])
            )
        ]),
    ]),
    ddk.Card(children=[
        ddk.Graph(id='figure-1', style={'height':300}),
    ]),
    ddk.Card(children=[
        ddk.Graph(id='figure-2', style={'height':300}), 
    ]),
    ddk.Card(children=[
        ddk.Graph(id='figure-3', style={'height':300}),
    ]),
    ddk.Card(children=[
        ddk.Graph(id='figure-4', style={'height':300}),
    ])
])


@app.callback(
    [
        Output('figure-1', 'figure'),
        Output('figure-2', 'figure'),
        Output('figure-3', 'figure'),
        Output('figure-4', 'figure')
    ],
    [
        Input('title-dropdown', 'value'),
        Input('go','data')
    ], 
    prevent_initial_call=True
)
def show_graph(value, ugo):
    if ugo is not None and value is not None and len(value) > 0:
        df = pd.read_json(json.loads(constants.redis_instance.hget("app-data", "DATASET")))
        figures = make_figures(df, value)
        return figures
    else:
        return no_update


def make_figures(df, value):
    df = df
    df = Info.plug_gaps(df, 'time', 'trajectory', ["latitude", "longitude"], 1.5)
    cvs = ds.Canvas(plot_width=500, plot_height=250)
    cdf = df[['ITime', value]]
    agg = cvs.line(cdf, x="ITime", y=value)
    agg_masked = agg.where(agg.values != 0)
    fig1 = px.imshow(agg_masked, color_continuous_scale="gray", origin='lower')
    fig1.update_layout(coloraxis_showscale=False, title='Image from Data Shader Mask')
    sdf = agg.to_pandas()
    pdf = sdf.unstack()
    qdf = pdf.to_frame().reset_index()
    qdf = qdf.loc[qdf['0'==True]]
    qdf = qdf[['ITime', value]]
    qdf['time'] = pd.to_datetime(qdf['ITime'])
    qdf.reset_index(inplace=True, drop=True)
    qdf['trajectory'] = 'platform'
    # qdf = Info.plug_gaps(qdf, 'time', 'trajectory', ['trajectory'], 1.5)
    fig2 = px.line(qdf, x='time', y=value, title='Data reconstructed from Data Shader Mask ' + str(qdf.shape[0]) + ' points.')
    fig4 = px.line(df, x='time', y=value, title='Orginal Data ' + str(df.shape[0]))
    df = df.sample(n=int(df.shape[0]*.1))
    df = df.sort_values('time')
    df.reset_index(drop=True, inplace=True)
    # df = Info.plug_gaps(df, 'time', 'trajectory', ['trajectory'], 1.5)
    fig3 = px.line(df, x='time', y=value, title='Sampled with pandas at n='+str(int(df.shape[0]*.1)))
    return [fig1, fig2, fig3, fig4]


@app.callback(
    Output('go', 'data'),
    Input('drone-dropdown',  'value')
)
def get_data(drone_id):
    if drone_id is not None and len(drone_id) > 0:
        url = data_url + drone_id + '.csv'
        print(url)
        df = pd.read_csv(url, skiprows=[1])
        df["ITime"] = pd.to_datetime(df["time"]).astype("int64")
        constants.redis_instance.hset("app-data", "DATASET", json.dumps(df.to_json(orient='records')))
        return 'go'
    else:
        return no_update


@app.callback (
    [
        Output('figure-1', 'figure', allow_duplicate=True),
        Output('figure-2', 'figure', allow_duplicate=True),
        Output('figure-3', 'figure', allow_duplicate=True),
        Output('figure-4', 'figure', allow_duplicate=True),
    ],
    [
        Input('figure-1', 'relayoutData'),
        Input('figure-2', 'relayoutData'),
        Input('figure-3', 'relayoutData'),
        Input('figure-4', 'relayoutData'),
        Input('reset', 'n_clicks'),
    ],
    [
        State('drone-dropdown',  'value')
    ], prevent_initial_call=True
)
def zoom_plots(update_1, update_2, update_3, update_4, in_reset, value):
    df = pd.read_json(json.loads(constants.redis_instance.hget("app-data", "DATASET")))
    if "reset" in callback_context.triggered_id:
        return make_figures(df, value)

    if 'figure-1' in callback_context.triggered_id:
        try:
            xmax = update_1["xaxis.range[1]"]
            xmin = update_1["xaxis.range[0]"]
            print('updating from plot 1', xmin, xmax)
            df_filtered = df.loc[(df["ITime"] < xmax) & (df["ITime"] > xmin)]
            print('filtered data set passed to make_figures has ', df_filtered.shape[0], ' points')
            figures = make_figures(df_filtered.copy(), value)
            return figures
        except Exception as e:
            return no_update
    elif 'figure-2' in callback_context.triggered_id:
        try:
            xmax = update_2["xaxis.range[1]"]
            xmin = update_2["xaxis.range[0]"]
            print('updating from plot 2', xmin, xmax)
            df_filtered = df.loc[(df["time"] < xmax) & (df["time"] > xmin)]
            figures = make_figures(df_filtered, value)
            return figures
        except Exception as e:
            return no_update
    elif 'figure-3' in callback_context.triggered_id:
        try:
            xmax = update_3["xaxis.range[1]"]
            xmin = update_3["xaxis.range[0]"]
            print('updating from plot 3', xmin, xmax)
            df_filtered = df.loc[(df["time"] < xmax) & (df["time"] > xmin)]
            figures = make_figures(df_filtered, value)
            return figures
        except Exception as e:
            return no_update
    elif 'figure-4' in callback_context.triggered_id:
        try:
            xmax = update_4["xaxis.range[1]"]
            xmin = update_4["xaxis.range[0]"]
            print('updating from plot 4', xmin, xmax)
            df_filtered = df.loc[((df["time"] < xmax)&(df["time"] > xmin))]
            print(df_filtered.head(100))
            figures = make_figures(df_filtered, value)
            return figures
        except Exception as e:
            return no_update
    else:
        return no_update


if __name__ == '__main__':
    app.run_server(debug=True)

