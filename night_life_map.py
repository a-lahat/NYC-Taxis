import pandas as pd
from sodapy import Socrata
import json
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import urllib
from urllib.request import urlopen


client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=100000)
# 263 rows
map_results = client.get("755u-8jsi", limit=1000)
map_results_df = pd.DataFrame.from_records(map_results)

start = 0  # Start at 0
chunk_size = 100000  # Fetch 100000 rows at a time
results = []  # Empty out our result list
record_count = 10000000  # TODO the total file has 83,645,528 rows
while True:
    # Fetch the set of records starting at 'start'
    results.extend(client.get("2upf-qytp",
                              where="trip_distance > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND "
                                    "date_extract_y(tpep_dropoff_datetime) = 2019 AND "
                                    "date_extract_dow(tpep_pickup_datetime) not between 1 and 3 AND "
                                    "date_extract_hh(tpep_pickup_datetime) not between 6 and 21",
                              select="PULocationID, date_extract_hh(tpep_pickup_datetime), "
                                     "date_extract_m(tpep_pickup_datetime)",
                              offset=start, limit=chunk_size))
    # Move up the starting record
    start = start + chunk_size
    # If we have fetched all of the records, exit while
    if start > record_count:
        break

# Convert the list into a data frame
df = pd.DataFrame.from_records(results)
df.columns = ['PULocationID', 'hour', 'month']

# Check that sample data is distributed along months/hours to be sufficient
plt.figure(figsize=(22, 10))
plotnum = 1
for cols in ['month', 'hour']:
    if plotnum == 1:
        axs = plt.subplot(1, 2, plotnum)
        sns.distplot(df[cols])
        plt.title('Month Sample Data Density\n', fontsize=18)
        plt.xlabel('Month', fontsize=16)
        plt.xticks(fontsize=16)
        plt.ylabel('Density', fontsize=16)
        plt.yticks(fontsize=16)
    else:
        axs = plt.subplot(1, 2, plotnum)
        sns.distplot(df[cols])
        plt.title('Hour Sample Data Density\n', fontsize=18)
        plt.xlabel('Hour', fontsize=16)
        plt.xticks(fontsize=16)
        plt.ylabel('Density', fontsize=16)
        plt.yticks(fontsize=16)
    plotnum += 1
plt.tight_layout()
plt.show()

# Generate PU df
df_PU = df.groupby(['PULocationID'], as_index=False).size()
df_PU.columns = ['PU', 'n']
df_PU['n'] = df_PU['n'].astype('int')
# subset to PULocationIDs that are above the 5th percentile
# df = df[df['n'] > np.percentile(df['n'], 5)] # TODO
df_PU = df_PU[df_PU['n'] > 50000]
# update record count
record_count_PU = df_PU['n'].sum()
df_PU = df_PU.merge(right=map_results_df[['location_id', 'borough', 'zone']], how='left', left_on='PU',
                    right_on='location_id').drop(columns=['location_id'])
df_PU.columns = ["PU", "n", "PU_borough", "PU_zone"]

# How many in each borough
per_borough = df_PU.groupby(by=['PU_borough'], as_index=False)['n'].sum()
per_borough.columns = ['PU_borough', 'total_per_borough']
print(per_borough)

df_borough = pd.DataFrame()
for borough in per_borough['PU_borough'].values:
    curr_borough = df_PU[df_PU['PU_borough'] == borough]
    curr_borough = curr_borough.groupby(by=['PU_zone'], as_index=False)['n'].sum()
    curr_n = per_borough[per_borough['PU_borough'] == borough]['total_per_borough'].values[0]
    curr_borough['percentage'] = round((curr_borough['n'] / curr_n * 100), 2).astype(str) + "%"
    curr_borough['borough'] = borough
    df_borough = df_borough.append(curr_borough.sort_values('percentage'))

df_borough.to_csv('df_borough_26_2_50k.csv', encoding = 'utf-8-sig', index=False)

# Generate df for PU locations - final map visualization
df_PU = df_PU.merge(right=per_borough, how='left', on='PU_borough')
# density column per borough
# df_PU['density'] = df_PU['size'] / df_PU['total_per_borough']
# density column - out of all the trips, how many where from this pu id
df_PU['density'] = df_PU['n'] / record_count_PU
df_PU['percentage'] = round((df_PU['density'] * 100), 2).astype(str) + "%"
# info column - for hover data
df_PU['hover'] = df_PU['PU_zone'] + ", " + df_PU['PU_borough']

# store the URL in url as parameter for urlopen
url = "https://data.cityofnewyork.us/api/geospatial/d3c5-ddgc?method=export&format=GeoJSON"
# store the response of URL
response = urlopen(url)
# storing the JSON response from url in data
nycmap = json.loads(response.read())

# Generate interactive density maps for night-life hours pick-up and drop-off locations
fig = px.choropleth_mapbox(df_PU,
                           geojson=nycmap,
                           locations="PU",
                           featureidkey="properties.location_id",
                           color="density",
                           color_continuous_scale="viridis",
                           mapbox_style="carto-positron",
                           zoom=9, center={"lat": 40.7, "lon": -73.9},
                           opacity=0.7,
                           hover_name="hover",
                           hover_data=["percentage"],
                           title="Night life pick-up locations density map"
                           )
plotly.offline.plot(fig, filename='myplot.html')
