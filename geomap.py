import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

data = gpd.read_file("https://data.cityofnewyork.us/api/geospatial/d3c5-ddgc?method=export&format=GeoJSON")
print(type(data))

#geoplot.polyplot(data, projection=gcrs.AlbersEqualArea(), edgecolor='darkgrey', facecolor='lightgrey', linewidth=.3,
#                 figsize=(12, 8))

data.plot()
