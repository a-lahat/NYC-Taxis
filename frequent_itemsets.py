import math
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns


client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=1000)

# 2upf-qytp = 2019, t29m-gskq 2018

########## Frequent itemsets 2019: if I'm picked up at X what are the chances I want to be dropped off at Y? ##########

start = 0  # Start at 0
chunk_size = 2000  # Fetch 2000 rows at a time
results = []  # Empty out our result list
# TODO PU/DO-ID should be between 1 and 262?
# TODO maybe just Manhattan?
record_count = client.get("2upf-qytp",
                          where="trip_distance > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
                          select="COUNT(*)")
record_count = math.floor(int(record_count[0]['COUNT']))
record_count = 500000  # TODO the total file has 83,645,528 rows

while True:
    # Fetch the set of records starting at 'start'
    results.extend(client.get("2upf-qytp",
                              where="trip_distance > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
                              select="PULocationID, DOLocationID",
                              offset=start, limit=chunk_size))
    # Move up the starting record
    start = start + chunk_size
    # If we have fetched all of the records, exit while
    if start > record_count:
        break

df = pd.DataFrame.from_records(results)
#df1 = [[df['PULocationID'][i], df['DOLocationID'][i]] for i in range(len(df))]
#te = TransactionEncoder()
#te_ary = te.fit(df1).transform(df1)
#df1 = pd.DataFrame(te_ary, columns=te.columns_)
#print(apriori(df1, min_support=0.6, use_colnames=True))

df_counts = df.groupby(['PULocationID', 'DOLocationID'], as_index=False).size()
df_counts.columns = ['PU', 'DO', 'count']
df_counts['count'] = df_counts['count'].astype('float')

# TODO remove start points that only have one ride leaving from them?

orig_dest = [[0 for i in range(265)] for j in range(265)]
for i in range(265):  # row
    for j in range(265):  # col
        curr = df_counts[(df_counts['PU'] == str(i + 1)) & (df_counts['DO'] == str(j + 1))]['count']
        if len(curr) != 0:
            orig_dest[i][j] = curr.values[0]

for i in range(265):  # row
    init_sum = sum(orig_dest[i])
    #if init_sum > 0:
    if init_sum > 1:    # more than one ride from this origin
        for j in range(265):  # col
            orig_dest[i][j] = orig_dest[i][j] / init_sum


#orig_dest = [orig_dest[i][j] / tot[i] for i in range(265) for j in range(265)]
#for i in range(265):  # row
#    for j in range(265):  # col
#        if orig_dest[i][j] > 0:
#            print("From: " + str(i+1) + " to: " + str(j+1) + " with prob: " + str(orig_dest[i][j]))
# TODO origin that no rides exit from?

data = pd.DataFrame(orig_dest)
heatmap_plot = sns.heatmap(data, center=0, cmap='gist_ncar')
#plt.show()
# TODO other heatmap
fig = px.imshow(orig_dest)
fig.show()

