import os
import osmium
import json
import sqlite3
import datetime

import argparse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from typing import Union
	from pathlib import Path

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
	'-ci', '--cinput',
	type=str,
	help='Path to input pbf file'
)
parser.add_argument(
	'-co', '--coutput',
	type=str,
	help='Path to output db file'
)
_ai = parser.add_argument(
	'-ai', '--add_indexes',
	type=str,  # bool
	default=True,
)
_ai.help = f'Add indexes for faster search default: {_ai.default}'


def init_args(args):
	if args.add_indexes in (True, 'Y', 'y', 'Yes', 'yes', 'True', 'true', '1'):
		args.add_indexes = True
	else:
		args.add_indexes = False
	if not args.coutput:
		fno = os.path.splitext(args.cinput)[0]
		fn = os.path.splitext(fno)[0]
		args.coutput = ''.join((fn, '.db'))
	if args.cinput == args.coutput:
		print('You want to save file with the same name as the input file!')
		exit(1)


class OsmHandler(osmium.SimpleHandler):
	def __init__(self, output: 'Union[str, Path]' = ''):
		osmium.SimpleHandler.__init__(self)
		self.conn = sqlite3.connect(':memory:')
		self.output = output if output else datetime.datetime.strftime(datetime.datetime.now(), "osm-%y-%m-%d-%H-%M-%S.db")
		self.conn_file = sqlite3.connect(self.output)
		self.cursor = self.conn.cursor()
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, lat REAL, lon REAL, tags TEXT)''')
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS ways (id INTEGER PRIMARY KEY, nodes INTEGER, tags TEXT)''')
		self.conn.commit()


	def node(self, n):
		self.cursor.execute('''INSERT INTO nodes (id, lat, lon, tags) VALUES (?, ?, ?, ?)''', (n.id, n.location.lat, n.location.lon, json.dumps(dict(n.tags))))
		self.conn.commit()


	def way(self, w):
		self.cursor.execute('''INSERT INTO ways (id, nodes, tags) VALUES (?, ?, ?)''', (w.id, ' '.join(map(str, w.nodes)), json.dumps(dict(w.tags))))
		self.conn.commit()


	def save(self):
		if self.output:
			self.conn.backup(self.conn_file)
		else:
			raise ValueError('No output file!')


	def add_indexes(self):
		self.cursor.execute('''CREATE INDEX "nodes index lat" ON "nodes" ( "lat" )''')
		self.cursor.execute('''CREATE INDEX "nodes index lon" ON "nodes" ( "lon" )''')


def osm2sqlite3(input_fpath: 'Union[str, Path]', output_fpath: 'Union[str, Path]', add_indexes: bool = True) -> bool:
	# Conversion by handler
	handler = OsmHandler(output_fpath)
	handler.apply_file(input_fpath)

	# Add indexes in db to speedup search
	if add_indexes:
		handler.add_indexes()
	handler.conn.commit()
	handler.save()
	handler.conn.close()

	return True


def main():
	args = parser.parse_args()

	osm2sqlite3(args.input, args.output, args.add_indexes)


if __name__ == '__main__':
	main()
