# GraphPlotUtility (Working Title)
# Mission Statement
The goal of this library is to provide a tool which accepts shape files and network files to create constrained, random coordinates for each data point. This can be useful for network and data scientists who wish to leverage Geographical Informational Systems (GIS) insights without compromising the privacy of their sources.
# Installation
TBD
## Dependencies
The features of this library are built upon the functionality provided by these dependencies:
- NetworkX (Graph utility)
- Netrd (Network utility)
- Pandas (Statistical analysis)
- Numpy (Mathematical utility)
- Matplotlib (Creating plots and figures)
- Fiona (GIS utility)
# Documentation
## Table of Contents
- [[#Data Sources]]
- [[#Functionality]]
- [[#Examples]]
## Data Sources
### Shape Files
This library uses the [GeoJSON standard](https://geojson.org) encoding for storing geographic coordinates. A short example of a GeoJSON file:
```
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [125.6, 10.1]
    },
    "properties": {
        "name": "Dinagat Islands"
    }
}
```
The full standard as listed on the Internet Engineering Task Force (IETF) website is here: https://datatracker.ietf.org/doc/html/rfc7946
## Functionality
## Examples
# Contributions and Licensing
This project is licensed under the GNU General Public License Version 3.0 (full text can be found in the LICENSE file). We also adhere to the definition of "Open Source" per the Open Source Initiative: https://opensource.org/osd. However, as the project is still pre-release, we will not be accepting contributions at this time.
