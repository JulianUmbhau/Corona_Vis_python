# %%
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
from flask import Flask
from data_functions import get_country_data, get_corona_data, merge_data


# %%

country_data = get_country_data()

corona_data = get_corona_data()

df = merge_data(corona_data,country_data)

day="2020-05-01"
def prep_data(day, df):
    tmp=df[df["Date"] == day]
    tmp['size'] = tmp['Confirmed'].apply(lambda x: (np.sqrt(x/100) + 1) if x > 500 else (np.log(x) / 2 + 1)).replace(np.NINF, 0)
    # Compute bubble color
    tmp['color'] = (tmp['Deaths']/tmp['Confirmed']).fillna(0).replace(np.inf , 0)

    return(tmp)

map_df = prep_data(day, df)


# %%

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Dashboard'

#df = pd.read_csv("test_data.csv", low_memory=False)

load_dotenv("./.env")
mapbox_token = os.getenv("MAPBOX_TOKEN")

def create_world_fig(map_df, mapbox_token):
    figure = go.Figure(
        data=go.Scattermapbox(
            lat=map_df["lat"].unique(),
            lon=map_df["lon"].unique(),
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=map_df["size"],
                color=map_df["color"],
                showscale=True,
                colorbar={
                    "title":"Fatality Rate",
                    "titleside":"top", 
                    "thickness":4, 
                    "ticksuffix":"%"
                    }),
            customdata=np.stack((map_df["Country"],map_df['Confirmed'],map_df['Deaths']),axis=0),
            hovertemplate=
            " <em> Country %{customdata[0]} </em><br>" + 
            "🚨  %{customdata[1]}<br>" +
            "⚰️  %{customdata[2]} "),
        layout=go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox= {
            "accesstoken": mapbox_token,
            "bearing" : 0,
            "center": {
                "lat": 38.92,
                "lon": -77.07
                },
            "pitch": 0,
            "zoom": 1
        }))
    
    return figure 

map = create_world_fig(map_df, mapbox_token)


# %%


options_countries = [{"label":x, "value":x} for x in df["Country"].unique()]
options_values = [
    {"label":"Confirmed", "value":"Confirmed"},
    {"label":"Deaths", "value":"Deaths"}
]



app.layout = html.Div(children=[
    html.H1(
        children='Choose Countries'
        ),
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
        "Confirmed cases and mortality rate on " + day,
        dcc.Graph(id = "mapping", figure=map)
    ]),
    # html.Div([
    #     "Choose value to show",
    #     dcc.RadioItems(
    #         id="value_choice_delta",
    #         options=options_values,
    #         value='Confirmed',
    #         labelStyle={'display': 'inline-block'}
    #     )
    # ]),

    # html.Br(),

    # html.Div([
    #     "Choose Countries to show",
    #     dcc.Dropdown(
    #         id="country_choice_delta",
    #         options = options_countries,
    #         value=["Denmark", "Sweden"],
    #         multi=True
    #     )
    # ]),

    # dcc.Graph(id="line_chart_delta"),

])

@app.callback(
    Output("line_chart_total", "figure"), 
    Input("country_choice_total", "value"),
    Input("value_choice_total", "value"))
def update_line_chart(country_choice_total, value_choice_total):
    countries_chosen_df_total = df.loc[df['Country'].isin(country_choice_total)]
    #countries_chosen_df = countries_chosen_df[["year", value_chosen]]
    fig = px.line(countries_chosen_df_total, x="Date", y=value_choice_total, color="Country", title="Corona - Total " + value_choice_total + " Cases")
    return fig

# @app.callback(
#     Output("line_chart_delta", "figure"), 
#     Input("country_choice_delta", "value"),
#     Input("value_choice_delta", "value"))
# def update_line_chart(country_choice_delta, value_choice_delta):
#     countries_chosen_df_delta = df.loc[df['Country'].isin(country_choice_delta)]
#     print(value_choice_delta)
#     if value_choice_delta=="Confirmed":
#         value_choice_delta="confirmed_delta"
#         value_text="Confirmed Delta"
#     elif value_choice_delta=="Deaths":
#         value_choice_delta="deaths_delta"
#         value_text="Deaths Delta"
#     fig = px.line(countries_chosen_df_delta, x="Date", y=value_choice_delta, color="Country", title="Corona " + value_text + " Cases")
#     fig = fig.update_layout(yaxis_title=value_text)
#     return fig

if __name__ == '__main__':
    app.run_server(debug=True)

# %%
