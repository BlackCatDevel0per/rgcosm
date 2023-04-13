import argparse

from convert import parser as conv_parser
from coordinates_to_address import parser as ltln_parser

parser = argparse.ArgumentParser(description='rgcosm cli', parents=[conv_parser, ltln_parser])

args = parser.parse_args()


# Geocoder add_indexes to bool conversion
if args.add_indexes in ('Y', 'y', 'Yes', 'yes', 'True', 'true'):
	args.add_indexes = True
else:
	args.add_indexes = False

# Converter
if args.cinput and args.coutput:
	from convert import osm2sqlite3
	osm2sqlite3(args.cinput, args.coutput, args.add_indexes)


# Geocoder
if args.database:
	from coordinates_to_address import coordinates_to_address
	if not args.latitude and not args.longitude:
		if not args.lat_lon:
			print('Give coordinates in lat & lon')
			exit(1)
		lat, lon = args.lat_lon.split()
		args.latitude = lat
		args.longitude = lon
	addr = coordinates_to_address(args.database, float(args.latitude), float(args.longitude))
	print(addr)
