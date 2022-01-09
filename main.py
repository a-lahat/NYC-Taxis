import math
import pandas as pd
from sodapy import Socrata
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.community.centrality import girvan_newman

client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=1000)

# 2upf-qytp = 2019, t29m-gskq 2018

# Communities 2019: get all pick-up --> drop-off ids
start = 0  # Start at 0
chunk_size = 2000  # Fetch 2000 rows at a time
results = []  # Empty out our result list
record_count = client.get("2upf-qytp",
                          where="trip_distance > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
                          select="COUNT(*)")
record_count = math.floor(int(record_count[0]['COUNT']))
record_count = 500000
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

# Convert the list into a data frame
df = pd.DataFrame.from_records(results)
df_counts = df.groupby(['PULocationID', 'DOLocationID'], as_index=False).size()
df_counts.columns = ['PU', 'DO', 'weight']
df_counts['weight'] = df_counts['weight'].astype('int')
# print(df_counts.sort_values(by=['weight'], ascending=True))
df_counts = df_counts[df_counts['weight'] > 1]

G = nx.Graph()
G = nx.from_pandas_edgelist(df_counts, source='PU', target='DO', edge_attr='weight')
communities = girvan_newman(G)

node_groups = []
for com in next(communities):
    node_groups.append(list(com))
print(len(node_groups))
print(node_groups)
color_map = []
some_colors = ['red', 'blue', 'green', 'yellow', 'purple']

# for i in range(len(node_groups)):
#    color_map.append([some_colors[i]]*len(node_groups[i]))

for node in G:
    if node in node_groups[0]:
        color_map.append(some_colors[0])
    elif node in node_groups[1]:
        color_map.append(some_colors[1])
    elif node in node_groups[2]:
        color_map.append(some_colors[2])
    elif node in node_groups[3]:
        color_map.append(some_colors[3])
    else:
        color_map.append(some_colors[4])
nx.draw(G, node_color=color_map, with_labels=True)
plt.show()
