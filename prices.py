import statistics
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt

client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=1000)

# 2upf-qytp = 2019, t29m-gskq 2018

########## Avg price per mile throughout hours of the day ##########

start = 0  # Start at 0
chunk_size = 2000  # Fetch 2000 rows at a time
results2019 = []  # Empty out our result list
results2018 = []
results2017 = []
# TODO PU/DO-ID should be between 1 and 262?
# record_count = client.get("2upf-qytp",
#                          where="trip_distance > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
#                          select="COUNT(*)")
# record_count = math.floor(int(record_count[0]['COUNT']))
record_count = 500000  # TODO the total file has 83,645,528 rows

while True:
    # Fetch the set of records starting at 'start'
    results2019.extend(client.get("2upf-qytp",
                                  where="trip_distance > 0 AND total_amount > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
                                  select="date_extract_hh(tpep_pickup_datetime), trip_distance, total_amount",
                                  offset=start, limit=chunk_size))  # TODO subtract tip_ammount?
    results2018.extend(client.get("t29m-gskq",
                                  where="trip_distance > 0 AND total_amount > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
                                  select="date_extract_hh(tpep_pickup_datetime), trip_distance, total_amount",
                                  offset=start, limit=chunk_size))
    results2017.extend(client.get("biws-g3hs",
                                  where="trip_distance > 0 AND total_amount > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
                                  select="date_extract_hh(tpep_pickup_datetime), trip_distance, total_amount",
                                  offset=start, limit=chunk_size))
    # Move up the starting record
    start = start + chunk_size
    # If we have fetched all of the records, exit while
    if start > record_count:
        break

df2019 = pd.DataFrame.from_records(results2019)
df2019.columns = ['hour', 'distance', 'price']
df2019['hour'] = df2019['hour'].astype('int')
df2019['distance'] = df2019['distance'].astype('float')
df2019['price'] = df2019['price'].astype('float')
df2019['avg'] = df2019['price'] / df2019['distance']
hours2019 = [statistics.mean(df2019[df2019['hour'] == i]['avg']) if i in list(df2019['hour']) else 0 for i in range(24)]

df2018 = pd.DataFrame.from_records(results2018)
df2018.columns = ['hour', 'distance', 'price']
df2018['hour'] = df2018['hour'].astype('int')
df2018['distance'] = df2018['distance'].astype('float')
df2018['price'] = df2018['price'].astype('float')
df2018['avg'] = df2018['price'] / df2018['distance']
hours2018 = [statistics.mean(df2018[df2018['hour'] == i]['avg']) if i in list(df2018['hour']) else 0 for i in range(24)]

df2017 = pd.DataFrame.from_records(results2017)
df2017.columns = ['hour', 'distance', 'price']
df2017['hour'] = df2017['hour'].astype('int')
df2017['distance'] = df2017['distance'].astype('float')
df2017['price'] = df2017['price'].astype('float')
df2017['avg'] = df2017['price'] / df2017['distance']
hours2017 = [statistics.mean(df2017[df2017['hour'] == i]['avg']) if i in list(df2017['hour']) else 0 for i in range(24)]

x = [*range(24)]

plt.plot(x, hours2017, label="2017")
plt.plot(x, hours2018, label="2018")
plt.plot(x, hours2019, label="2019")
plt.legend()
plt.show()

# print(df2019.groupby(['hour']).size())
# print(max(df2019.groupby(['hour']).size()))
# print(df2019.groupby(['hour']).size().idxmax())
# print(df2019[df2019['hour'] == df2019.groupby(['hour']).size().idxmax()]['avg'])
# print(sum(df2019[df2019['hour'] == df2019.groupby(['hour']).size().idxmax()]['avg']))
# print(statistics.mean(df2019[df2019['hour'] == df2019.groupby(['hour']).size().idxmax()]['avg']))
