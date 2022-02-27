from sodapy import Socrata
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import seaborn as sns

client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=1000)
airport_ids = client.get("755u-8jsi", where="zone='Newark Airport' OR zone='JFK Airport' OR zone='LaGuardia Airport'",
                         select='zone, location_id', limit=270)
airport_ids = pd.DataFrame.from_records(airport_ids)
print(airport_ids)

start = 0  # Start at 0
chunk_size = 25  # Fetch 25 rows at each hour
results = []  # Empty out our result list

for hour in range(0, 24):
    where_str = "trip_distance > 0.00 AND " \
                "date_extract_y(tpep_pickup_datetime) = 2019 AND " \
                "date_extract_y(tpep_dropoff_datetime) = 2019 AND " \
                "PULocationID = 1 OR PULocationID = 132 OR PULocationID = 138 AND " \
                "date_extract_hh(tpep_pickup_datetime) = " + str(hour)

    # Fetch the set of records starting at 'start'
    results.extend(client.get("2upf-qytp",
                              where=where_str,
                              select="PULocationID, tpep_pickup_datetime, tpep_dropoff_datetime, "
                                     "total_amount, passenger_count, trip_distance",
                              offset=start, limit=chunk_size))
    # Move up the starting record
    start = start + chunk_size

# Convert the list into a data frame
df = pd.DataFrame.from_records(results)
df.columns = ['location_id', 'PU_time', 'DO_time', 'total_amount', 'passenger_count', 'trip_distance']
df['trip_distance'] = df['trip_distance'].astype('float64')
df['total_amount'] = df['total_amount'].astype('float64')
df = df[df['trip_distance'] > 0.01]
df['price_per_mile'] = df['total_amount'] / df['trip_distance']

df['PU_time'] = pd.to_datetime(df['PU_time'], format='%Y-%m-%dT%H:%M:%S.%f')
df['PU_minute'] = ((df['PU_time'].dt.hour * 60) + df['PU_time'].dt.minute + (df['PU_time'].dt.second / 60)).round(
    decimals=2)
df['DO_time'] = pd.to_datetime(df['DO_time'], format='%Y-%m-%dT%H:%M:%S.%f')
df['trip_duration'] = (df['DO_time'] - df['PU_time']).dt.total_seconds() / 60

# Sanitation - trip_duration > 0, price_per_mile > 0, remove huge outliers from price_per_mile
df = df.loc[
    (df['price_per_mile'] > 0) & (df['price_per_mile'] < 10) & (df['trip_duration'] < 180) & (df['trip_distance'] < 50)]

# Clustering trip_distance VS trip_duration
x_input = df.loc[:, ['trip_distance', 'trip_duration']].values
# elbow
wcss = []
for k in range(1, 12):
    k_means = KMeans(n_clusters=k, init='k-means++')
    k_means.fit(x_input)
    wcss.append(k_means.inertia_)
plt.figure(figsize=(15, 8))
plt.plot(range(1, 12), wcss, linewidth=2, marker='8')
plt.title('Elbow method\n', fontsize=18)
plt.xlabel('K', fontsize=16)
plt.xticks(fontsize=16)
plt.ylabel('WCSS', fontsize=16)
plt.yticks(fontsize=16)
# clustering
k_means = KMeans(n_clusters=4)
labels = k_means.fit_predict(x_input)
plt.figure(figsize=(16, 10))
plt.scatter(x_input[:, 0], x_input[:, 1], c=k_means.labels_, s=105)
# plt.scatter(k_means.cluster_centers_[:, 0], k_means.cluster_centers_[:, 1], color='red', s=250)
plt.title('Airport Trip clusters\n', fontsize=20)
plt.xlabel('Trip Distance (miles)', fontsize=16)
plt.xticks(fontsize=16)
plt.ylabel('Trip Duration (minutes)', fontsize=16)
plt.yticks(fontsize=16)

plt.show()

df['label'] = labels
duration_40_to_60 = df.loc[(df['label']==1) & (df['trip_distance'] < 20) & (df['trip_distance'] > 15)]
duration_20_to_40 = df.loc[(df['label']==2) & (df['trip_distance'] < 20) & (df['trip_distance'] > 15)]
sns.distplot(duration_40_to_60['PU_time'].dt.hour)
sns.distplot(duration_20_to_40['PU_time'].dt.hour)

plt.show()

