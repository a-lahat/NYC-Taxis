import math
import pandas as pd
from sodapy import Socrata
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.community.centrality import girvan_newman
from networkx.algorithms.community import k_clique_communities
from scipy import stats

import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import seaborn as sns

client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=1000)

# 2upf-qytp = 2019, t29m-gskq 2018

####################### Communities 2019: get all pick-up --> drop-off ids #######################

start = 0  # Start at 0
chunk_size = 2000  # Fetch 2000 rows at a time
results = []  # Empty out our result list
# record_count = client.get("2upf-qytp",
#                          where="trip_distance > 0 AND date_extract_y(tpep_pickup_datetime) = 2019 AND date_extract_y(tpep_dropoff_datetime) = 2019",
#                          select="COUNT(*)")
# record_count = math.floor(int(record_count[0]['COUNT']))
record_count = 2000000  # TODO the total file has 83,645,528 rows
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
df_counts.columns = ['PU', 'DO', 'n']
df_counts['PU'] = df_counts['PU'].astype('int')
df_counts['DO'] = df_counts['DO'].astype('int')
df_counts['n'] = df_counts['n'].astype('int')
df_counts = df_counts[df_counts['n'] > 100].reset_index(drop=True)

# if p < 0.05 then distribution of num of rides from x to y isn't normal
shapiro_test = stats.shapiro(list(df_counts['n']))
print(shapiro_test.pvalue)
# plt.hist(df_counts['n'])

# outlier removal
Q1 = df_counts['n'].quantile([0.25]).values[0]
Q3 = df_counts['n'].quantile([0.75]).values[0]
IQR = Q3 - Q1
# df_counts = df_counts[~((df_counts['n'] < Q1-1.5*IQR) | (df_counts['n'] > Q3+1.5*IQR))].reset_index()
df_counts = df_counts[~(df_counts['n'] < Q1 - 1.5 * IQR)].reset_index(drop=True)
# rerun shapiro
shapiro_test = stats.shapiro(list(df_counts['n']))
print(shapiro_test.pvalue)
print("Q1: " + str(Q1) + " ,Q3: " + str(Q3))
# plt.hist(df_counts['n'])
# plt.show()

#sns.pairplot(df_counts)

# not normal, rank pairs
df_counts['rank'] = df_counts['n'].rank()
print(df_counts[df_counts['n'] >= 1000])
print("MAX: " + str(max(df_counts['rank'])) + " rank 1000: " + str(df_counts[df_counts['n'] == 1000]))

# U-test to find p-value of 1000 rides



# Community detection
G = nx.from_pandas_edgelist(df_counts[['PU', 'DO']], source='PU', target='DO', create_using=nx.DiGraph())

# communities = k_clique_communities(G, k=5)
communities = girvan_newman(G)
# communities = list(communities)

# girvan_dendrogram(communities)

node_groups = []
for com in next(communities):
    node_groups.append(list(com))
print(len(node_groups))
print(node_groups)
color_map = []
some_colors = ['red', 'blue', 'green', 'yellow', 'purple']

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
