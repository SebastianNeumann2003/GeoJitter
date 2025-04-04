### Sources so you can get stuff if I get the wrong format

#### Regions
- [Chicago downtown neighborhoods](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Neighborhoods/bbvz-uum9)
- [Chicago downtown wards](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Wards-2015-2023-/sp34-6z76)

- [GADM](https://gadm.org/maps.html)
  - Any country / down to county ish level. Seems a bit messy.

- [USA Census](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html)

#### Networks
- [US Rail](https://data-usdot.opendata.arcgis.com/datasets/usdot%3A%3Anorth-american-rail-network-nodes/about)
  - This has rail stations across the us. It doesn't have edges... but maybe it is easy to add the closest 2 nodes + any that are within 10% of that radius.
  - We should note this is probably a 'worst case' on how much perturbation will screw up edge distribution etc, since it is a highly constrained network.
  - us_rail_network.pkl is a networkx graph with node attributes 'lat' and 'long' and edge attributes 'distance'. It is pretty big (249968 Nodes, 595231 Edges), with edges selected as suggested in the first bullet in this list. It may be reasonable to pare it down to a few different states (using your check within boundary functions for a state boundary), then doing any experiments on counties etc within the state.
- [Brightkite](https://snap.stanford.edu/data/loc-Brightkite.html)
  - spatial_graph_brightkite.pkl is a networkx graph with node attributes 'lat' and 'long'with 50686 nodes and 194090 edges where links represent social interactions among social network users and locations are averages of node location when using the app.
- [Gowalla](https://snap.stanford.edu/data/loc-Gowalla.html)
  - spatial_graph_gowalla.pkl is a networkx graph with node attributes 'lat' and 'long' with 107068 nodes and 456761 edges where links represent social interactions among social network users and locations are averages of node location when using the app.