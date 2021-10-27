# %%
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
import os
import geopandas as gpd

geo_df = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))


df = pd.read_csv("test_data.csv", low_memory=False)

load_dotenv("./.env")
mapbox_token = os.getenv("MAPBOX_TOKEN")

biosfera = dlx.geojson_to_geobuf(dlx.dicts_to_geojson([dict(lat=29.015, lon=-118.271)]))

#def update_map(mapbox_token):

map = go.Figure(go.Scattermapbox(
    lat=df["lat"].unique(),
    lon=df["lon"].unique(),
    mode="markers",
    marker=go.scattermapbox.Marker(
        size=9
        ),
    text=df["Country"].unique()
))

map.update_layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_token,
        bearing=0,
        center=dict(
            lat=38.92,
            lon=-77.07
        ),
        pitch=0,
        zoom=1
    ),
)


#map = update_map(mapbox_token)

app = dash.Dash(__name__)

options_countries = [{"label":x, "value":x} for x in df["Country"].unique()]
options_values = [
    {"label":"Confirmed", "value":"Confirmed"},
    {"label":"Deaths", "value":"Deaths"}
]

app.layout = html.Div(children=[
    html.H1(children='Choose Countries'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    html.Br(),

    html.Div([
        "Choose value to show",
        dcc.RadioItems(
            id="value_choice_total",
            options=options_values,
            value='Confirmed',
            labelStyle={'display': 'inline-block'}
        )
    ]),

    html.Br(),

    html.Div([
        "Choose Countries to show",
        dcc.Dropdown(
            id="country_choice_total",
            options = options_countries,
            value=["Denmark", "Sweden"],
            multi=True
        )
    ]),

    dcc.Graph(id="line_chart_total"),

        html.Br(),

    html.Div([
        "Choose value to show",
        dcc.RadioItems(
            id="value_choice_delta",
            options=options_values,
            value='Confirmed',
            labelStyle={'display': 'inline-block'}
        )
    ]),

    html.Br(),

    html.Div([
        "Choose Countries to show",
        dcc.Dropdown(
            id="country_choice_delta",
            options = options_countries,
            value=["Denmark", "Sweden"],
            multi=True
        )
    ]),

    dcc.Graph(id="line_chart_delta"),

    dl.Map(children=[
        dl.TileLayer(), 
        dl.GeoJSON(data=biosfera, format="geobuf")
        ],  # in-memory geobuf (smaller payload than geojson)
        style={'width': '1000px', 'height': '500px'}),

    dcc.Graph(figure=map)

])

@app.callback(
    Output("line_chart_total", "figure"), 
    Input("country_choice_total", "value"),
    Input("value_choice_total", "value"))
def update_line_chart(country_choice_total, value_choice_total):
    countries_chosen_df = df.loc[df['Country'].isin(country_choice_total)]
    #countries_chosen_df = countries_chosen_df[["year", value_chosen]]
    fig = px.line(countries_chosen_df, x="Date", y=value_choice_total, color="Country", title="Corona - Total " + value_choice_total + " Cases")
    return fig

@app.callback(
    Output("line_chart_delta", "figure"), 
    Input("country_choice_delta", "value"),
    Input("value_choice_delta", "value"))
def update_line_chart(country_choice_delta, value_choice_delta):
    countries_chosen_df = df.loc[df['Country'].isin(country_choice_delta)]
    if value_choice_delta=="Confirmed":
        value_choice_delta="confirmed_delta"
        value_text="Confirmed Delta"
    elif value_choice_delta=="Deaths":
        value_choice_delta="deaths_delta"
        value_text="Deaths Delta"
    fig = px.line(countries_chosen_df, x="Date", y=value_choice_delta, color="Country", title="Corona " + value_text + " Cases")
    fig = fig.update_layout(yaxis_title=value_text)
    return fig


#if __name__ == '__main__':
app.run_server(debug=True)
