# RGCosm - Reverse Geocode for OpenStreetmap
[![Upload Python Package](https://github.com/BlackCatDevel0per/rgcosm/actions/workflows/python-publish.yml/badge.svg)](https://github.com/BlackCatDevel0per/rgcosm/actions/workflows/python-publish.yml)

A Python library for offline reverse geocoding from osm(.pbf) GIS converted to sqlite3 data - based on code from [rgcoms scripts](https://github.com/punnerud/rgcosm)

### Install by:
```bash
pip install rgcoms
```
or from source by:
```bash
git clone https://github.com/BlackCatDevel0per/rgcosm
cd rgcoms
pip install build
python -m build
```

### Dependencies
1. osmium

### CLI
See cli commands by:
```bash
python rgcosm -h
```
output:
```bash
usage: rgcosm [-h] [-ci CINPUT] [-co COUTPUT] [-ai ADD_INDEXES] [-db DATABASE]
                   [-ltln LAT_LON] [-lat LATITUDE] [-lon LONGITUDE] [-st SEARCH_TAGS]
                   [-mtc MIN_TAGS_COUNT] [-rd RETRIEVE_DEGREE] [-rt ROUND_TO]

rgcosm cli

optional arguments:
  -h, --help            show this help message and exit
  -ci CINPUT, --cinput CINPUT
                        Path to input pbf file
  -co COUTPUT, --coutput COUTPUT
                        Path to output db file
  -ai ADD_INDEXES, --add_indexes ADD_INDEXES
                        Add indexes for faster search default: True
  -db DATABASE, --database DATABASE
                        Path to db file
  -ltln LAT_LON, --lat_lon LAT_LON
                        latitude with longitude separated by space
  -lat LATITUDE, --latitude LATITUDE
                        latitude
  -lon LONGITUDE, --longitude LONGITUDE
                        longitude
  -st SEARCH_TAGS, --search_tags SEARCH_TAGS
                        tags to search, default: `addr:`
  -mtc MIN_TAGS_COUNT, --min_tags_count MIN_TAGS_COUNT
                        Minimal tags count (for `-st/--search_tags`) to filter result,
                        default: 1
  -rd RETRIEVE_DEGREE, --retrieve_degree RETRIEVE_DEGREE
                        Retrieve addresses within a +/- x degree range of the original
                        coordinates, default: 0.001
  -rt ROUND_TO, --round_to ROUND_TO
                        Round degree to n decimals after dot, default: 8
```

### First convert downloaded osm(.pbf) files from:
https://download.geofabrik.de/

Then use cli to create the database (speedupped by using db in ram & dump in to disk):
```bash
python rgcosm -ci some-place.osm.pbf -co some-place.db
```

The output file can be x7-13 (for maldives file ~12.74 times) times larger then the source file, for example [maldives](https://download.geofabrik.de/asia/maldives-latest.osm.pbf) file size is 2.7 mb, and after conversion size increased to 34.4 mb (time: ~14 sec.) with added indexes and 20.1 mb without (time: ~13 sec.).

You can disable adding indexes by `-ai=no` or `--add_indexes=no` arg.

Adding indexes speedups searching time up to 70 times.

### Usage
```python
from rgcosm import get_address
db_path = 'maldives-latest.db'
coordinates = (6.5506617, 72.9530232)
addr = get_address(db_path, coordinates)
print(addr)
```
result:
```python
[{'id': 9508099415, 'lat': 6.5506617, 'lon': 72.9530232, 'tags': {'addr:block_number': '26', 'generator:method': 'combustion', 'generator:output:electricity': '200 kV', 'generator:source': 'diesel', 'name': 'Vaikaradhoo Fenaka Power Plant 3', 'operator': 'Fenaka Corporation Limited Vaikaradhoo', 'power': 'generator'}}]
```
or with multiple coordinates:
```python
from rgcosm import get_address
db_path = 'maldives-latest.db'
coordinates = [(6.5506617, 72.9530232), (4.172474, 73.5083067), (4.1718557, 73.5154427)]
addr = get_address(db_path, coordinates)
print(addr)
```
result:
```python
[{'id': 9508099415, 'lat': 6.5506617, 'lon': 72.9530232, 'tags': {'addr:block_number': '26', 'generator:method': 'combustion', 'generator:output:electricity': '200 kV', 'generator:source': 'diesel', 'name': 'Vaikaradhoo Fenaka Power Plant 3', 'operator': 'Fenaka Corporation Limited Vaikaradhoo', 'power': 'generator'}}, {'id': 2521220337, 'lat': 4.172474, 'lon': 73.5083067, 'tags': {'addr:city': "Male'", 'addr:housename': 'Ma.Seventy Flower', 'addr:street': 'Iskandharu Magu', 'amenity': 'cafe', 'cuisine': 'coffee_shop', 'internet_access': 'yes', 'name': "Chili's Café"}}, {'id': 7987147424, 'lat': 4.1718557, 'lon': 73.5154427, 'tags': {'addr:city': "Male'", 'addr:housenumber': 'H.Hostside', 'addr:postcode': '20053', 'addr:street': 'Irudheymaa Hingun', 'clothes': 'women;wedding;men;suits;fashion;children', 'contact:facebook': 'https://m.facebook.com/Aiccet/', 'currency:EUR': 'yes', 'currency:GBP': 'yes', 'currency:USD': 'yes', 'name': 'Aiccet', 'opening_hours': '24/7', 'operator': 'Aiccet', 'payment:american_express': 'yes', 'payment:cash': 'yes', 'payment:credit_cards': 'yes', 'payment:mastercard': 'yes', 'payment:visa': 'yes', 'payment:visa_debit': 'yes', 'phone': '+960 7997323', 'shop': 'clothes'}}]
```

Advanced (for keep connection to db):
```python
from rgcosm import RGeocoder
db_path = 'maldives-latest.db'
geo = RGeocoder(db_path)
coordinates = [(4.1758869, 73.5094013), (-0.6699146, 73.1228688), (5.159217, 73.1312907)]
addrs = geo.locate(coordinates, 'addr:', 1)
print(addrs)
```
result:
```python
[{'id': 10300135473, 'lat': 4.1758869, 'lon': 73.5094013, 'tags': {'addr:city': "Male'", 'email': 'silverlinehotelsupplier@gmail.com', 'name': 'Silverline Hotel Supplies', 'office': 'company', 'phone': '732-9577', 'website': 'http://www.silverlineenterprise.com/'}}, {'id': 9446166886, 'lat': -0.6699146, 'lon': 73.1228688, 'tags': {'addr:city': 'Addu City', 'addr:housenumber': 'Mushkuraanaage', 'addr:postcode': '19030', 'addr:street': 'Dhandivara Maga'}}, {'id': 8439302155, 'lat': 5.159217, 'lon': 73.1312907, 'tags': {'addr:city': 'Dharavandhoo', 'addr:postcode': '06060', 'amenity': 'courthouse', 'name': 'Dharavandhoo Magistrate Court', 'opening_hours': 'Sa-Th 08:00-14:00', 'operator': 'Government of Maldives'}}]
```

### In plans:
- [ ] db serializing with lz4 compression & etc.
- [ ] Add more formats for addresses
- [ ] Add caching results
- [ ] More speedup conversion & less memory usage
- [ ] Add some features from other similar libs
- [ ] More documentation

