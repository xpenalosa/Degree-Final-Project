from __future__ import print_function

import logging
from kazoo.client import KazooClient

class TornejosAPI():
	"""API for the tournament managing website.
	
	
	"""

	def __init__(self, client):
		self.client = client
		self.path = '/zookeeper/tornejos'

	def create_tournament(self, name, version, players, password):
		"""Create a new tournament zNode
		
		Creates a new node in the zookeeper database that corresponds
		to a tournament. The information stored per zNode is a string
		containing a json structure with the following format:
			Tournament
				{
					'name' : <string[32]>,
					'version' : <integer>,
					'password' : <string[16]>,
					'editable' : <bool>
					'deletion_date' : <string[10]> (dd/mm/yyyy)
				}
		The zNode will have multiple children, each corresponding to a
		player participating in the tournament.
		"""
		self.client.ensure_path(self.path)

	
	def __create_player(self, path, player):
		"""Create a new player zNode

		Creates a new node in the zookeeper database that corresponds
		to a player. The information stored per zNode is a string
		containing a json structure with the following format:
			Player
				{
					'name' : <string[16]>,
					'points' : <integer>,
					'disqualified' : <bool>,
					'wins' : <integer>,
					'losses' : <integer>
				}
		"""
