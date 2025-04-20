import pickle
from typing import Hashable

import networkx as nx
import geopandas as gp
import shapely as shp
import matplotlib.pyplot as plt
import contextily as ctx

import geojitter as gj

fig, ax = plt.subplots()

with open("./experiments/data/networks/spatial_graph_brightkite", "rb") as f:
    big_network: nx.Graph = pickle.load(f)

all_states = gp.read_file("./data_vault/cb_2018_us_state_20m/cb_2018_us_state_20m.shp").get(['STATEFP', 'NAME', 'geometry'])
all_states.crs = "EPSG:4326"

congress = gp.read_file("./data_vault/cb_2023_us_sldl_500k/cb_2023_us_sldl_500k.shp")
congress.crs = "EPSG:4326"
geo_missouri = all_states.loc[all_states['NAME'] == 'Missouri', 'geometry']

trial_states = ['Texas', 'Virginia', 'California', 'New York', 'Missouri']


for trial_state in trial_states:
    def point_converter(node: Hashable, data: dict) -> tuple[float, float]:
        return (data['long'], data['lat'])

    def region_accessor_tile(node: Hashable) -> shp.Polygon:
        if "region" not in focused_network_tile.nodes(data=True)[node]:
            return tiled_regions[0]
        else:
            region_name = focused_network_tile.nodes(data=True)[node]["region"]
            return tiled_regions[region_name]

    def region_accessor_congress(node: Hashable) -> shp.Polygon:
        if "region" not in focused_network_congress.nodes(data=True)[node]:
            return congress_regions.iloc[0].iloc[0]
        else:
            region_name = focused_network_congress.nodes(data=True)[node]["region"]
            return congress_regions.iloc[region_name].iloc[0]

    state_subdf = all_states.loc[all_states['NAME'] == trial_state, ['STATEFP', 'geometry']]
    fips = state_subdf.iloc[0].iloc[0]
    state_geom = state_subdf.iloc[0].iloc[1]

    focused_network_tile: nx.Graph = gj.filter_network_by_region(big_network, state_geom)
    focused_network_congress: nx.Graph = focused_network_tile.copy()

    tiled_regions: gp.GeoSeries = gj.gen_region_grid_rc(focused_network_tile, 10, 10)
    congress_regions: gp.GeoDataFrame = congress.loc[congress['STATEFP'] == fips]

    jittered_by_radius = gj.obfuscated_network(
        regions=None,
        network=focused_network_tile,
        region_accessor=lambda x: x,
        point_converter=point_converter,
        strategy=gj.rand_point_by_radius(0.5),
        fail_graceful=False
    )

    jittered_by_tile = gj.obfuscated_network(
        regions=tiled_regions,
        network=focused_network_tile,
        region_accessor=region_accessor_tile,
        point_converter=point_converter,
        strategy=gj.rand_point_in_region(),
        fail_graceful=False
    )

    jittered_by_congress = gj.obfuscated_network(
        regions=congress_regions,
        network=focused_network_congress,
        region_accessor=region_accessor_congress,
        point_converter=point_converter,
        strategy=gj.rand_point_in_region(),
        fail_graceful=False
    )

    print(trial_state, "is done!")
