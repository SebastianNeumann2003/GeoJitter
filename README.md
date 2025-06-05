# GeoJitter
# Mission Statement
The goal of this library is to provide a lighweight tool which accepts geolocated network files and randomly anonymizes the network's point locations with respect to the regions they began in.
# Installation
On release, this library will be available using a install via `pip`. At this time, we have a test release available using TestPyPi. It can be installed with the following command:
```
pip install -i https://test.pypi.org/simple/ geojitter
```
## Dependencies
The features of this library are built upon the functionality provided by these dependencies:
- [NetworkX][networkx]
- [GeoPandas][geopandas]
- [Shapely][shapely]
- [Contextily][contextily]
- [Scipy][scipy]
- [Numpy][numpy]
- [Matplotlib][matplotlib]
- [Triangle][triangle]
# Documentation
## Table of Contents
<!-- TODO -->

## Data Sources
One input is strictly necessary for all functionality: a network. This is expected to be a `networkx` `Graph` or one of its subclasses (`MultiGraph`, `DiGraph`, etc.). Also generally recommended is a collection of regions, expected to be in the form of a `geopandas` `GeoDataFrame`.

## Example
This is an explanantion of the execution of [boston_example.py](https://github.com/SeabassTheFish03/GeoJitter/blob/main/boston_example.py) found in this repository. It is a narrow example of how `GeoJitter` can be used.

First, the data is obtained by reading two files. The network file is [test_network1.pkl](https://github.com/SeabassTheFish03/GeoJitter/blob/main/data_vault/test_network1.pkl), a pickled network in the form of a `NetworkX` `Graph`. The region file is read using the `geopandas.read_file` function from [2020 Census Data](https://github,com/SeabassTheFish03/GeoJitter/blob/main/data_vault/Boston_Neighborhood_Boundaries_Approximated_by_2020_Census_Tracts.shp) and stored as a `GeoDataFrame`, which is then pruned into a dictionary containing only the name of each neighborhood and the `Polygon` data associated with it.

After setting up the visualization, two functions are defined. These are used for translating the data into a form `GeoJitter` can read. The `region_accessor` accepts the name of a region and returns its associated `Polygon`. The `point_converter` accepts the name of a node and its data from the `Graph`, then returns a `Point` reflecting that. In this example, the data does not include the original point locations, so the function is hard-coded to return the point `(0, 0)`. This will be overwritten during the jittering process. However, in other data sets where points are not already associated with regions, those regions can be inferred using a point's position.

Then, two new networks are generated from the data and displayed. This network generates a figure similar to the one shown below:
<p align="center">
    <img src="https://raw.githubusercontent.com/SeabassTheFish03/GeoJitter/refs/heads/main/boston_network.png" alt="Example network post-jitter">
</p>
# Contributions and Licensing
This project is licensed under the GNU General Public License Version 3.0 (full text can be found in the LICENSE file). We also adhere to the definition of "Open Source" per the Open Source Initiative: https://opensource.org/osd. However, as the project is still pre-release, we will not be accepting contributions at this time.

<!--
Link References
-->
[networkx]:https://github.com/networkx/networkx
[geopandas]:https://github.com/geopandas/geopandas
[numpy]:https://github.com/numpy/numpy
[matplotlib]:https://github.com/matplotlib/matplotlib
[triangle]:https://github.com/drufat/triangle
[contextily]:https://github.com/geopandas/contextily
[shapely]:https://github.com/shapely/shapely
[scipy]:https://github.com/scipy/scipy
