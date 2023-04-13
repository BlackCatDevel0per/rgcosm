import sqlite3
import math

import argparse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from typing import Union
	from pathlib import Path

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
	'-db', '--database',
	type=str,
	help='Path to db file'
)
parser.add_argument(
	'-ltln', '--lat_lon',
	type=str,
	help='latitude with longitude separated by space'
)
parser.add_argument(
	'-lat', '--latitude',
	type=str,
	help='latitude'
)
parser.add_argument(
	'-lon', '--longitude',
	type=str,
	help='Path to output db file'
)


def coordinates_to_address(db_path: 'Union[str, Path]', lat, lon, search_args: str = 'addr:') -> 'Optional[dict]':
	# Connect to the database
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Retrieve addresses within a +/- 0.01 degree range of the original coordinates
	cursor.execute('''
		SELECT id, lat, lon, tags
		FROM nodes
		WHERE lat >= ? AND lat <= ? AND lon >= ? AND lon <= ?
	''', (lat - 0.001, lat + 0.001, lon - 0.001, lon + 0.001))
	rows = cursor.fetchall()
	# print('Found nodes:', len(rows))
	if len(rows) == 0:
		conn.close()
		return None

	# Find the address with the smallest distance from the original coordinates
	min_distance = float('inf')
	min_address = None
	for row in rows:
		_id, node_lat, node_lon, tags = row
		distance = math.sqrt((node_lat - lat) ** 2 + (node_lon - lon) ** 2)
		# if tags.count('addr:'):
		# 	print(tags.count('addr:'))
		if distance < min_distance:
			if tags.count(search_args) >= 2:
				min_distance = distance
				min_address = {'id': _id, 'lat': node_lat, 'lon': node_lon, 'tags': tags}

	# Parse the tags column to find the address
	#address = {}
	#for tag in min_address['tags'].split(','):
	#    k, v = tag.split(':', 1)
	#    address[k] = v

	# Close the connection to the database
	conn.close()

	# Return the address
	return min_address


def main():
	args = parser.parse_args()

	if not args.latitude and not args.longitude:
		if not args.lat_lon:
			print('Give coordinates in lat & lon')
			exit(1)
		lat, lon = args.lat_lon.split()
		args.latitude = lat
		args.longitude = lon
	addr = coordinates_to_address(args.database, float(args.latitude), float(args.longitude))
	print(addr)
