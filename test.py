# %%
import dash
import dash_leaflet as dl
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

df = pd.read_csv("test_data.csv", low_memory=False)

app = dash.Dash(__name__)

options_countries = [{"label":x, "value":x} for x in df["Country"].unique()]

app.layout = html.Div(children=[
    html.H1(children='Choose Countries'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    html.Div([
        "Choose country to show",
        dcc.RadioItems(
            id="value_choice",
            options=options_countries,
            value='Denmark',
            labelStyle={'display': 'inline-block'}
        )
    ]),

    html.Div([
        "Choose Countries to show",
        dcc.Dropdown(
            id="country_choice",
            options = options_countries,
            value=["Denmark"],
            multi=True
        )
    ]),

    dcc.Graph(id="line-chart"),

    dl.Map(dl.TileLayer(), style={'width': '1000px', 'height': '500px'})

])

@app.callback(
    Output("my-multi-dynamic-dropdown", "options"),
    Input("my-multi-dynamic-dropdown", "search_value"),
    State("my-multi-dynamic-dropdown", "value")
)
def update_multi_options(search_value, value):
    if not search_value:
        raise PreventUpdate
    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.
    return [
        o for o in options_countries if search_value in o["label"] or o["value"] in (value or [])
    ]

@app.callback(
    Output("line-chart", "figure"), 
    Input("country_choice", "value"))
def update_line_chart(value_chosen):
    countries_chosen_df = df.loc[df['Country'].isin(value_chosen)]
    #countries_chosen_df = countries_chosen_df[["year", value_chosen]]
    fig = px.line(countries_chosen_df, x="Date", y="Confirmed")
    return fig


#if __name__ == '__main__':
app.run_server(debug=True)
