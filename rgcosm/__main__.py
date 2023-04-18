import sys

if len(sys.argv) == 1:
	print('Help: rgosm -h/--help')
	exit(1)

import argparse

from .convert import parser as conv_parser
from .geocoder import parser as ltln_parser

parser = argparse.ArgumentParser(prog='rgcosm', description='rgcosm cli', parents=[conv_parser, ltln_parser])

args = parser.parse_args()


# Converter
if args.cinput:
	from .convert import osm2sqlite3
	from .convert import init_args as converter_init_args
	converter_init_args(args)
	osm2sqlite3(args.cinput, args.coutput, args.add_indexes)


# Geocoder
elif args.database:
	from .geocoder import get_address
	from .geocoder import init_args as geocoder_init_args
	geocoder_init_args(args)
	addr = get_address(args.database, (args.latitude, args.longitude), args.search_tags, args.min_tags_count, args.retrieve_degree, args.round_to)
	print(addr)

