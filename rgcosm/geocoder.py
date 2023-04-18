import sqlite3
from pathlib import Path
import json
import math

import argparse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from typing import Union, Optional
	from typing import Mapping
	from pathlib import Path

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
	'-db', '--database',
	type=str,
	default='convert_output.db',
	help='Path to db file'
)
parser.add_argument(
	'-ltln', '--lat_lon',
	type=str,  # separated by space
	help='latitude with longitude separated by space'
)
parser.add_argument(
	'-lat', '--latitude',
	type=str,  # float
	help='latitude'
)
parser.add_argument(
	'-lon', '--longitude',
	type=str,  # float
	help='longitude'
)
_st = parser.add_argument(
	'-st', '--search_tags',
	type=str,
	default='addr:'
)
_st.help = f'tags to search, default: `{_st.default}`'
_mtc = parser.add_argument(
	'-mtc', '--min_tags_count',
	type=int,
	default=1
)
_mtc.help = f'Minimal tags count (for `{_st.option_strings[0]}/{_st.option_strings[1]}`) to filter result, default: {_mtc.default}'
_rd = parser.add_argument(
	'-rd', '--retrieve_degree',
	type=float,
	default=0.001
)
_rd.help = f'Retrieve addresses within a +/- x degree range of the original coordinates, default: {_rd.default}'
_rt = parser.add_argument(
	'-rt', '--round_to',
	type=int,
	default=8
)
_rt.help = f'Round degree to n decimals after dot, default: {_rt.default}'


def init_args(args):
	if not args.latitude and not args.longitude:
		if not args.lat_lon:
			print('Give coordinates in lat & lon')
			exit(1)
		lat, lon = args.lat_lon.split()
		args.latitude = lat
		args.longitude = lon
	args.latitude = float(args.latitude)
	args.longitude = float(args.longitude)


class RGeocoder():
	def __init__(self, db_path: 'Union[str, Path]'):
		# Connect to the database
		if not Path(db_path).exists():
			self.conn = None
			raise FileNotFoundError(f'DB file `{db_path}` does not exist!')
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()


	def find(self, lat: float, lon: float, search_tags: str = 'addr:', min_tags_count: int = 1, retrieve_degree: float = 0.001, round_to: int = 8) -> 'Optional[dict]':
		self.cursor.execute('''
			SELECT id, lat, lon, tags
			FROM nodes
			WHERE lat >= ? AND lat <= ? AND lon >= ? AND lon <= ?
		''', (
			# Retrieve addresses within a +/- `retrieve_degree` degree range of the original coordinates
			# round degree to `round_to` decimals after dot
			round(lat - retrieve_degree, round_to), round(lat + retrieve_degree, round_to),
			round(lon - retrieve_degree, round_to), round(lon + retrieve_degree, round_to)
			)
		)
		rows = self.cursor.fetchall()
		# print('Found nodes:', len(rows))
		if len(rows) == 0:
			return None

		# Find the address with the smallest distance from the original coordinates
		min_distance = float('inf')
		min_address = None
		for row in rows:
			_id, node_lat, node_lon, tags = row
			distance = math.sqrt((node_lat - lat) ** 2 + (node_lon - lon) ** 2)
			# if tags.count(search_tags):
			# 	print(tags.count(search_tags))
			if distance < min_distance:
				if tags.count(search_tags) >= min_tags_count:
					min_distance = distance
					min_address = {'id': _id, 'lat': node_lat, 'lon': node_lon, 'tags': tags}

		# Parse the tags column to find the address
		#address = {}
		#for tag in min_address['tags'].split(','):
		#    k, v = tag.split(':', 1)
		#    address[k] = v

		if min_address:
			min_address['tags'] = json.loads(min_address['tags'])

		# Return the address
		return min_address


	def locate(self, coordinates: 'Union[Mapping[float, float], Mapping[Tuple[float, float]]]',
		search_tags: str = 'addr:', min_tags_count: int = 1, retrieve_degree: float = 0.001, round_to: int = 8) -> 'Optional[List[dict]]':
		if hasattr(coordinates, '__getitem__'):
			if isinstance(coordinates[0], float):
				coordinates = [coordinates]
		addresses = []
		for lat, lon in coordinates:
			min_address = self.find(lat, lon, search_tags, min_tags_count, retrieve_degree, round_to)
			if min_address:
				addresses.append(min_address)
		return addresses if addresses else None


	def __del__(self):
		if self.conn:
			self.conn.close()
			del self.cursor
			del self.conn


	def __enter__(self):
		return self


	def __exit__(self, exc_type, exc_value, traceback):
		self.__del__()



def get_address(db_path: 'Union[str, Path]', coordinates: 'Union[Mapping[float, float], Mapping[Tuple[float, float]]]',
	search_tags: str = 'addr:', min_tags_count: int = 1, retrieve_degree: float = 0.001, round_to: int = 8) -> 'Optional[List[dict]]':
	geo = RGeocoder(db_path)
	return geo.locate(coordinates, search_tags, min_tags_count, retrieve_degree, round_to)


def main():
	args = parser.parse_args()
	init_args(args)

	addr = get_address(args.database, float(args.latitude), float(args.longitude))
	print(addr)
