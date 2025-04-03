# GeoJitter
# Mission Statement
The goal of this library is to provide a tool which accepts shape files and network files to create constrained, random coordinates for each data point. This can be useful for network and data scientists who wish to leverage Geographical Informational Systems (GIS) insights without compromising the privacy of their sources.
# Installation
On release, this library will be available using a install via `pip`. While still in development, we have an easy install script available.
## Windows
Ensure you have `git` and `python` installed and added to your `PATH` environment variable. Then, after cloning this repository, navigate to the top-level directory (the one with this `README.md` file in it) and enter the following command:
```
>.\install.bat
```
(The `>` character is the default prompt character and should not be included)
### Linux/MacOS
Ensure you have `git` and `python` installed and added to your `PATH` environment variable. Then, after cloning this repository, navigate to the top-level directory (the one with this `README.md` file in it) and enter the follwing commands:
```
$ chmod +x install.sh
$ ./install.sh
```
(The `$` character is the default prompt charactyer and should not be included)
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
The main purpose of this library is to ambiguate GIS data while preserving meaningful analytic insights to some level of detail. Most of this functionality can be accessed through importing the netgeo package into your project. The `netgeo.py` file contains all the top-level functions intended for use in a larger projcet.
## Examples
# Contributions and Licensing
This project is licensed under the GNU General Public License Version 3.0 (full text can be found in the LICENSE file). We also adhere to the definition of "Open Source" per the Open Source Initiative: https://opensource.org/osd. However, as the project is still pre-release, we will not be accepting contributions at this time.
