# %%
import dash
import dash_leaflet as dl
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

df = px.data.gapminder()

app = dash.Dash(__name__)

options = [
    {"label":"Sweden", "value":"Sweden"},
    {"label":"Denmark", "value":"Denmark"}
    ]

app.layout = html.Div(children=[
    html.H1(children='Choose Countries'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    html.Div(children = "</br>"),

    html.Div([
        "Choose country to show",
        dcc.RadioItems(
            id="value_choice",
            options=options,
            value='Denmark',
            labelStyle={'display': 'inline-block'}
        )
    ]),

    dcc.Graph(id="line-chart"),

    dcc.Dropdown(
    options=[
        {'label': 'New York City', 'value': 'NYC'},
        {'label': 'Montreal', 'value': 'MTL'},
        {'label': 'San Francisco', 'value': 'SF'}
    ],
    value=['MTL', 'NYC'],
    multi=True),

    dl.Map(dl.TileLayer(), style={'width': '1000px', 'height': '500px'})

])

@app.callback(
    Output("line-chart", "figure"), 
    Input("value_choice", "value"))
def update_line_chart(value_chosen):
    countries_chosen_df = df.loc[df['country'].isin([value_chosen])]
    #countries_chosen_df = countries_chosen_df[["year", value_chosen]]
    fig = px.line(countries_chosen_df, 
        x="year", y="pop", color='country')
    return fig

#if __name__ == '__main__':
app.run_server(debug=True)
