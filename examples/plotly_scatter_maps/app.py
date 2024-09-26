from dash import Dash, dcc
import dash_design_kit as ddk
import plotly.express as px
import plotly.graph_objects as go

import colorcet as cc

import pandas as pd

from sdig.util import zc

app = Dash(__name__)
server = app.server  # expose server variable for Procfile

url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/global_dms_database.csv?time%2Clatitude%2Clongitude%2Cplatform&distinct()'
df = pd.read_csv(url, skiprows=[1])

df = df.sample(n=5000)
df['platform'] = df['platform'].apply(lambda x: x.split('(')[0])

df = df.sort_values('platform')

zoom, center = zc.zoom_center(lons=df['longitude'], lats=df['latitude'])

slippy_map = go.Figure()
platforms = df['platform'].unique()
for idx, platform in enumerate(platforms):
    mdf = df.loc[df['platform']==platform]
    color = cc.b_glasbey_bw[idx]
    trace = go.Scattermap(lat=mdf['latitude'], lon=mdf['longitude'], marker={'color': color}, name=platform)
    slippy_map.add_trace (trace)

slippy_map.update_layout(
        legend_title='Platform',
        hoverlabel={'namelength' :-1},
        legend_orientation="v",
        legend_x=1.,
        height=1000,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        map_style="white-bg",
        map_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                # "sourceattribution": "Powered by Esri",
                "sourceattribution": "GEBCO; NOAA/NCEI",
                "source": [
                    # "https://ibasemaps-api.arcgis.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}?token=" + constants.ESRI_API_KEY
                    'https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/GEBCO_basemap_NCEI/MapServer/tile/{z}/{y}/{x}'
                ]
            }
        ],
        mapbox_zoom=zoom,
        mapbox_center=center,
    )

slippy_px = px.scatter_map(df, lat='latitude', lon='longitude', color='platform', zoom=zoom, center=center, height=1000, color_discrete_sequence=cc.b_glasbey_bw)

lambert = px.scatter_geo(df, lat='latitude', lon='longitude', color='platform', color_discrete_sequence=cc.b_glasbey_bw)
lambert.update_layout(height=1000,)
lambert.update_geos(showcoastlines=True, coastlinecolor="RebeccaPurple",
                            showland=True, landcolor="LightGreen",
                            showocean=True, oceancolor="Azure",
                            showlakes=True, lakecolor="Blue", 
                            resolution=50,)

app.layout = ddk.App([
    dcc.Tabs([
        dcc.Tab(label='Tile Map with Default Map Libre Basemap', children=[
            dcc.Graph(
                figure=slippy_px
            )
        ]),
        dcc.Tab(label='"Geo" map with Lambert Equal Area Projection', children=[
            dcc.Graph(
                figure=lambert
            )
        ]),
        dcc.Tab(label='NOAA Bathymetry Tiles', children=[
            dcc.Graph(
                figure=slippy_map
            )
        ]),
    ])
])

if __name__ == '__main__':
    app.run(debug=True)