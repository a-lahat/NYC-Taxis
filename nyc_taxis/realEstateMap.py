import networkx as nx
import statistics
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from pandas.tseries.holiday import USFederalHolidayCalendar
from random import randrange
from fuzzywuzzy import fuzz
from urllib.request import urlopen
import json
from shapely.geometry import shape, mapping
from shapely.geometry import Point
import sys
import plotly.express as px


with urlopen('https://data.cityofnewyork.us/api/geospatial/d3c5-ddgc?method=export&format=GeoJSON') as response:
    nycmap = json.load(response)


client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=100000)
results = client.get("5ebm-myj7",
                     where="type_of_home = '01 ONE FAMILY HOMES' AND year = '2017'",
                    select='borough, neighborhood, median_sale_price, year', limit=100000
                    )
df = pd.DataFrame.from_records(results)
df['median_sale_price'] = pd.to_numeric(df['median_sale_price'])
df['year'] = pd.to_numeric(df['year'])


taxiAreaResult = client.get("755u-8jsi",
                    select='location_id, zone, borough', limit=100000
                    )
df_taxiArea = pd.DataFrame.from_records(taxiAreaResult)
df_taxiArea['location_id'] = pd.to_numeric(df_taxiArea['location_id'])

#add location id to df from df_taxi
dict = {
    "KINGSBRIDGE HTS/UNIV HTS": "Kingsbridge Heights",
    "OLD MILL BASIN": "Marine Park/Mill Basin",
    "AIRPORT LA GUARDIA": "LaGuardia Airport",
    "ST. ALBANS": "Saint Albans",
    "CASTLETON CORNERS": "Charleston/Tottenville",
    "RICHMONDTOWN-LIGHTHS HILL": "Richmond Hill",
    "ROSSVILLE-CHARLESTON": "Charleston/Tottenville",
    "CASTLE HILL/UNIONPORT": "Soundview/Castle Hill",
    "OLD MILL BASIN": "Marine Park/Mill Basin",
    "ARROCHAR-SHORE ACRES": "Arrochar/Fort Wadsworth",
    "UPPER WEST SIDE (79-96)": "Upper West Side South",
    "UPPER EAST SIDE (79-96)": "Upper East Side North",
    "CASTLE HILL/UNIONPORT": "Soundview/Castle Hill"
}

# add location id to df from df_taxi
tuples_list = []
for i in df['neighborhood']:
    maxToken = 0
    neighborhood_name = ""
    for j in df_taxiArea['zone']:
        fuzzT = fuzz.token_set_ratio(i, j)
        if fuzz.token_set_ratio(i, j) > maxToken:
            maxToken = fuzzT
            neighborhood_name = j
    if maxToken < 90:
        if i in dict:
            neighborhood_name = dict[i]
        else:
            neighborhood_name = ""
    tuples_list.append(neighborhood_name)
# tuples_list = [max([(fuzz.token_set_ratio(i,j),j) for j in df_taxiArea['zone']]) for i in df['neighborhood']]
print(tuples_list)
# tuples_list = [i[1] for i in tuples_list]
location_id = []
for i in tuples_list:
    x = df_taxiArea.loc[df_taxiArea["zone"] == i]
    if x.empty:
        location_id.append(0)
    else:
        x.reset_index()
        location_id.append(x.iloc[0]['location_id'])
print(tuples_list)
print(location_id)
print(len(tuples_list))
df['id'] = location_id


# Generate interactive density maps for night-life hours pick-up and drop-off locations
fig = px.choropleth_mapbox(df,
                           geojson=nycmap,
                           locations="id",
                           featureidkey="properties.location_id",
                           color="median_sale_price",
                           range_color=(0, 4000000),
                           color_continuous_scale="viridis",
                           mapbox_style="carto-positron",
                           zoom=9, center={"lat": 40.7, "lon": -73.9},
                           opacity=0.7,
                           # hover_name="hover",
                           # hover_data=["percentage"],
                           title="Night life pick-up locations density map"
                           )
# plotly.offline.plot(fig)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
plt.show()
