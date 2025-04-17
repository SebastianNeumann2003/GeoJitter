import pickle
import networkx as nx
import geopandas as gp
import shapely as shp
import matplotlib.pyplot as plt
import contextily as ctx

import geojitter as gj

regions: gp.GeoDataFrame = gp.read_file("./data_vault/cb_2018_us_state_20m/cb_2018_us_state_20m.shp")
nevada = regions.loc[36, 'geometry']
