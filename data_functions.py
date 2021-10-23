# %%
from json import load
from math import isnan
import pandas as pd
from pandas.core.algorithms import duplicated, isin
import numpy as np
import requests
from bs4 import BeautifulSoup
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

# %%

url = "https://www.worldometers.info/world-population/population-by-country/"

page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

headers = soup.find_all("th")
columns = []
for head in headers:
    temp = head.text
    columns.append(head.text)

tr = soup.find(id = "example2")

tds = tr.find_all("td")

df = pd.DataFrame(columns=columns)
temp = []
i = 0
for td in tds:
    i += 1
    temp.append(td.text)
    if i > 11:
        temp = pd.Series(temp, index=columns)
        df = df.append(temp, ignore_index=True)
        temp = []
        i = 0

df['Yearly Change'] = df['Yearly Change'].str.replace('%','')
df['Urban Pop %'] = df['Urban Pop %'].str.replace('%','')
df['World Share'] = df['World Share'].str.replace('%','')

df = df.rename(columns={df.columns[1]:"Country", df.columns[2]:"Population"})

df = df.drop(df.columns[[0]], axis=1)  # df.columns is zero-based pd.Index

df.reset_index(drop=True,inplace=True)


# %%

def clean_data(data, value):
        
    data_clean = data.rename(columns = {'Long':'lon', "Lat":"lat", 'Country/Region':'Country'})
    data_country_locations = data_clean[pd.isna(data_clean["Province/State"])][["Country", "lat", "lon"]]
    data_clean = data_clean.drop(columns=["Province/State"])

    data_clean["Country"] = data_clean["Country"].str.replace("US", "United States")
    data_clean["Country"] = data_clean["Country"].str.replace("Korea, South", "South Korea")
    
    data_clean = data_clean.melt(id_vars=["Country", "lat","lon"], var_name=["Date"], value_name=value)
    data_clean["Date"] = pd.to_datetime(data_clean["Date"], errors="coerce")
    data_clean = data_clean.groupby(["Country", "Date"]).sum().reset_index()
    
    for country in data_country_locations["Country"]:
        lat = data_country_locations[data_country_locations["Country"] == country]["lat"]
        lon = data_country_locations[data_country_locations["Country"] == country]["lon"]
        data_clean["lat"].loc[data_clean["Country"] == country] = lat.item()
        data_clean["lon"].loc[data_clean["Country"] == country] = lon.item()
    return(data_clean)


url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

deaths = pd.read_csv(url_deaths)
confirmed = pd.read_csv(url_confirmed)

deaths_clean = clean_data(data=deaths, value="Deaths")
confirmed_clean = clean_data(data=confirmed, value="Confirmed")

confirmed_clean = confirmed_clean.drop(columns=["Date", "Country","lat","lon"])
confirmed_deaths_clean = deaths_clean.join(confirmed_clean)

confirmed_deaths_clean_population = pd.merge(confirmed_deaths_clean, df, on=["Country"])

#confirmed_deaths_clean_population["Delta_confirmed"] = confirmed_deaths_clean_population.groupby("Country").

# used before function definition for caching of returned data
@st.cache 
def create_delta_values(confirmed_deaths_clean_population):
    confirmed_deaths_result = pd.DataFrame()
    for country in confirmed_deaths_clean_population["Country"].unique():
        temp = confirmed_deaths_clean_population[confirmed_deaths_clean_population["Country"] == country]
        temp["deaths_delta"] = ""
        temp["confirmed_delta"] = ""
        for i in range(0, len(temp)):
            if i == 0:
                temp["deaths_delta"].iloc[i] = temp["Deaths"].iloc[i]
                temp["confirmed_delta"].iloc[i] = temp["Confirmed"].iloc[i]
            else:
                temp["deaths_delta"].iloc[i] = temp["Deaths"].iloc[i] - temp["Deaths"].iloc[i-1]
                temp["confirmed_delta"].iloc[i] = temp["Confirmed"].iloc[i] - temp["Confirmed"].iloc[i-1]
        confirmed_deaths_result = confirmed_deaths_result.append(temp)
        print(country)
    return(confirmed_deaths_result)

confirmed_deaths_clean = create_delta_values(confirmed_deaths_clean_population)

# %%
# TODO Datamanipulation: fjerne minus i delta, rolling average, percentage of population, cases per 100.000 pop,  
# TODO: Map visualization, user input, forecasting, 
# TODO: Excess mortality - data?
# TODO: Improve performance of delta loop

# %%

import dash
import dash_leaflet as dl

app = dash.Dash()
app.layout = dl.Map(dl.TileLayer(), style={'width': '1000px', 'height': '500px'})

if __name__ == '__main__':
    app.run_server() 







# %%
st.header("Choose Countries")

col1, col2 = st.columns(2)
countries_chosen_total_cases = col1.multiselect("Select Countries", list(confirmed_deaths_clean["Country"].unique()), default=["Denmark"], key="multiselect1")
value_choice = col2.radio("Deaths or confirmed cases", ["Confirmed", "Deaths"], key="radio1")

####

countries_chosen_df = confirmed_deaths_clean.loc[confirmed_deaths_clean['Country'].isin(countries_chosen_total_cases)]
countries_chosen_df = countries_chosen_df[["Date", value_choice]]
countries_chosen_df["Date"] = countries_chosen_df["Date"].dt.strftime('%d/%m/%Y')
c1 = px.line(countries_chosen_df, x="Date", y=value_choice, title='Cases')
st.plotly_chart(c1)


#### 
col3, col4 = st.columns(2)
countries_chosen_delta_cases = col3.multiselect("Select Countries", list(confirmed_deaths_clean["Country"].unique()), default=["Denmark"], key="multiselect2")
value_choice = col4.radio("Deaths or confirmed cases", ["Confirmed", "Deaths"], key="radio2")
value_choice = value_choice.lower() + "_delta"

countries_chosen_df = confirmed_deaths_clean.loc[confirmed_deaths_clean['Country'].isin(countries_chosen_total_cases)]
countries_chosen_df = countries_chosen_df[["Date", value_choice]]
countries_chosen_df["Date"] = countries_chosen_df["Date"].dt.strftime('%d/%m/%Y')
c2 = px.line(countries_chosen_df, x="Date", y=value_choice, title='Delta cases')
st.plotly_chart(c2)

forecasting_horizon_chosen = st.slider("Forecasting horizon", 5, 100, 5)

# %%
# Mapbox visualization

col5, col6 = st.columns(2)
countries_chosen_map = col5.multiselect("Select Countries", list(confirmed_deaths_clean["Country"].unique()), default=["Denmark"], key="multiselect3")
value_choice = col6.radio("Deaths or confirmed cases", ["Confirmed", "Deaths"], key="radio3")
date_choice = st.date_input("Choose Date", max(confirmed_deaths_clean["Date"]), min(confirmed_deaths_clean["Date"]), max(confirmed_deaths_clean["Date"]))
countries_chosen_df = confirmed_deaths_clean.loc[confirmed_deaths_clean['Country'].isin(countries_chosen_map)]

countries_chosen_df = confirmed_deaths_clean
countries_chosen_df = countries_chosen_df[countries_chosen_df["Date"] == date_choice.strftime("%d/%m/%Y")]

countries_chosen_df = countries_chosen_df[countries_chosen_df["Country"] == "Denmark"]

countries_chosen_df = countries_chosen_df[["Country","lat","lon"]]

st.map(countries_chosen_df)

# %%

#countries_chosen_df = countries_chosen_df.set_index("Date")

# %%
st.text("End")


# %%
