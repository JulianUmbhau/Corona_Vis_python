# %%
import pandas as pd
from pandas.core.algorithms import duplicated
import numpy as np
import requests
from bs4 import BeautifulSoup
import streamlit as st
import plotly.express as px

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

url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

deaths = pd.read_csv(url_deaths)
confirmed = pd.read_csv(url_confirmed)

# %%
deaths_clean = deaths.drop(columns=["Province/State","Lat", "Long"])

import matplotlib.pyplot as plt

#deaths_clean.reset_index().rename(columns={"index":"ID"})

deaths_clean.melt(id_vars=["Country/Region"], var_name="Date")



deaths_clean[["Country/Region"]]

deaths_clean.columns()

deaths_clean["Angola"].plot()

deaths_clean.plot()

deaths_clean = deaths_clean.set_index("Country/Region")

deaths_clean=deaths_clean.rename(columns = {'Country/Region':'country'})

deaths_clean = deaths_clean.T

deaths_clean.reset_index()

deaths_clean = pd.DataFrame(deaths_clean.groupby(["country"]).sum())


deaths_clean["country"].duplicated()

deaths_clean = deaths_clean.drop_duplicates(subset=['country'])

deaths_long = pd.wide_to_long(deaths_clean, stubnames="", i="Country/Region", j="Date")
df2=pd.melt(deaths_clean,id_vars=['Country/Region'], var_name='Date', value_name='Deaths')

df2.columns


#df2["Date"] = pd.to_datetime(df2["Date"])

# @st.cache used before function definition for caching of returned data

# %%
df2_test = df2[df2["Country/Region"] == "Albania"]
df2_test = df2_test.drop(columns=["Country/Region"])
#df2_test = df2_test.astype(str)

# %%
st.dataframe(df2_test.head())
st.header("Test timeline")

#df2["Deaths"] = int(df2["Deaths"])

#st.line_chart(df2_test)

# add together duplicatd countries
# deaths_clean["Country/Region"][deaths_clean["Country/Region"].duplicated()].unique()
# deaths_clean[deaths_clean["Country/Region"].duplicated()]

# %%
