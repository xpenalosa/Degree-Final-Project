#!/usr/bin/python3
import logging
from datetime import datetime, timedelta
import json
import re

from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock, ReadLock
from kazoo.exceptions import LockTimeout, NoNodeError

from data_api.errors import DataApiErrors, DataApiException


class DataAPI():
	"""Data API for the tournament managing website.
	
	
	"""

	MATCH_STATUS = {
		"UNPLAYED" : "U",
		"P1_WON" : "1",
		"P2_WON" : "2" }

	def __init__(self, client):
		self.client = client
		self.path = "/tornejos"
	

	def __get_tournament_path(self, tournament_id):
		"""Get the path to the specified tournament's zNode."""
		t_id = '0'*(10-len(tournament_id)) + tournament_id
		tournament_path = self.path + "/t" + t_id
		return tournament_path


	def __create_tournament(self,
			name, modality, password, player_amount):
		"""Create a new tournament zNode.

		Creates a new node in the zookeeper database that corresponds
		to a tournament. The information stored per zNode is a string
		containing a json structure with the following format:
			Tournament
				{
					'name' : <string[32]>,
					'modality' : <integer>,
					'password' : <string[16]>,
					'classification' : <string[128]>,
					'deletion_date' : <string[10]>
							  (dd/mm/yyyy)
				}

		On success returns the created tournament path.
		"""
		# Calculate deletion date and format to dd/mm/yyyy
		deletion_date = datetime.now() + timedelta(days=30)
		formatted_deletion_date = deletion_date.strftime("%d/%m/%Y")

		# Calculate amount of matches
		matches = player_amount - 1
		# Initialize the classification to Unplayed for every match
		classification = self.MATCH_STATUS["UNPLAYED"] * matches
		
		# Concatenate the data into a dictionary
		tournament_dict = {
			'name' : name,
			'modality' : modality,
			'password' : password,
			'classification': classification,
			'deletion_date' : formatted_deletion_date}
		# Create a json dump with the object
		tournament_data = str.encode(json.dumps(tournament_dict))
		# Store the data in the transaction object
		tournament_path = self.client.create(
			self.path + "/t", value=tournament_data, sequence=True)
		return tournament_path
		
	
	def __create_player(self, transaction, tournament_path, player):
		"""Create a new player zNode

		Creates a new node in the zookeeper database that corresponds
		to a player. The information stored per zNode is a string
		containing a json structure with the following format:
			Player
				{
					'name' : <string[16]>,
					'points' : <integer>,
					'disqualified' : <integer>,
					'wins' : <integer>,
					'losses' : <integer>
				}
		"""
		player_dict = {
			'name' : player,
			'points' : 0,
			'disqualified' : 0,
			'wins' : 0,
			'losses' : 0}
		player_data = str.encode(json.dumps(player_dict))
		transaction.create(tournament_path + "/p",
			value=player_data, sequence=True)


	def __delete_tournament(self, tournament_path):
		"""Delete a tournament zNode and all its children

		Tries to delete the zNode located in the specified path.
		If the node does not exist, no exceptions are raised.
		"""
		try:
			self.client.delete(tournament_path, recursive=True)
		except NoNodeError:
			pass
		return 0


	def set_data_path(self, path):
		"""Set the path used to create the nodes."""
		self.path = path
		self.client.ensure_path(self.path)


	def create_tournament(self, name=None, modality=0, password=None,
			players=None):
		"""Create a new tournament with the players.
		
		The zNode will have multiple children, each corresponding to a
		player participating in the tournament.

		On success returns the created tournament path.
		"""
		# Add a tournament node
		tournament_path = self.__create_tournament(
			name, modality, password, len(players))
	
		# Spawn a transaction to add all the players	
		transaction = self.client.transaction()
		# Add all the players to transaction
		for player in players:
			self.__create_player(transaction, tournament_path,
				player)
		# Commit all the changes to ZooKeeper
		transaction_results = transaction.commit()

		# Verify all players were created correctly
		for result in transaction_results:
			if type(result) not in [str,bytes]:
				# Error, delete tournament node
				self.client.delete(tournament_path)
				# Return error
				raise DataApiException(
					DataApiErrors.ZOOKEEPER_ERROR)
		
		return tournament_path
	

	def delete_tournament(self, tournament_id, password):
		"""Delete an existing tournament
		
		The tournament is matched against its password and on a
		successful validation, the tournament and all its players are
		deleted.

		On success returns 0.
		"""
		tournament_path = self.__get_tournament_path(tournament_id)

		# Lock the node to ensure nobody is modifying it
		lock = self.client.Lock(tournament_path, self.client.client_id)
		try:
			lock.acquire(timeout=0.5)
			# Get data from the node
			data, stats = self.client.get(tournament_path)
			# Decode it
			data_dict = json.loads(data.decode())
			# Verify password matches
			if data_dict['password'] != password:
				# Raise error
				raise DataApiException(
					DataApiErrors.PASSWORD_MISMATCH)
			else:
				# Delete node
				self.client.delete(tournament_path,
					recursive=True)
		except LockTimeout as e:
			raise DataApiException(DataApiErrors.LOCK_TIMEOUT)
		finally:
			# Release lock regardless of outcome
			lock.release()

		return 0


	def get_tournament(self, tournament_id):
		"""Get the information about the tournament

		Retrieve the information about the current classification of
		the players.
		Returns a dictionary with the following format:
			data = {
				'name' : <string>,
				'classification' : <string>,
				'modality' : <integer>
				'version' : <integer>
				'players' : [
					'name' : <string>,
					'points' : <integer>,
					'disqualified' : <integer>,
					'wins' : <string>,
					'losses' : <string>
					]
				}
		"""
		tournament_path = self.__get_tournament_path(tournament_id)
		lock = self.client.ReadLock(tournament_path,
			self.client.client_id)
		data = dict()
		try:
			lock.acquire(timeout=0.5)
			# Get tournament data
			t_data, t_stats = self.client.get(tournament_path)
			# Unpack json
			t_json = json.loads(t_data.decode())
			# Get select fields
			data['name'] = t_json['name']
			data['classification'] = t_json['classification']
			data['modality'] = t_json['modality']
			data['version'] = t_stats.version
			# Get info about children
			player_ids = self.client.get_children(
				tournament_path)
			players_data = []
			player_id_regex = re.compile("^p\d{10}$")
			# Iterate over children
			for p_id in player_ids:
				# Skip read/write locks, treated as children
				if not player_id_regex.match(p_id):
					continue
				# Get data
				p_data, _ = self.client.get(tournament_path
					+ "/" + p_id)
				# Unpack json
				p_json = json.loads(p_data.decode())
				# Append to data dictionary
				players_data.append(p_json)
			data['players'] = players_data
		except LockTimeout as e:
			# Could not acquire lock
			raise DataApiException(DataApiErrors.LOCK_TIMEOUT)
		finally:
			# Release lock regardless of outcome
			lock.release()
		return data


	def update_tournament(self, tournament_id, version, classification,
			password):
		"""Update the classification of a tournament

		
		"""
		# Verify classification values
		for value in classification:
			if value not in self.MATCH_STATUS.values():
				raise DataApiException(
					DataApiErrors.CLASSIFICATION_VALUE)
		# Get tournament path
		tournament_path = self.__get_tournament_path(tournament_id)
		# Lock zNode
		lock = self.client.Lock(tournament_path, self.client.client_id)
		try:
			lock.acquire(timeout=0.5)
			# Get tournament data
			t_data, t_stats = self.client.get(tournament_path)
			# Verify node version
			if t_stats.version != version:
				raise DataApiException(
					DataApiErrors.VERSION_MISMATCH)

			# Subtract lock children from count
			t_child_nolock = t_stats.children_count - 1
			# Verify classification string length (Players - 1)
			if len(classification) != t_child_nolock - 1:
				raise DataApiException(
					DataApiErrors.CLASSIFICATION_LENGTH)
			# Verify password
			t_json = json.loads(t_data.decode())
			if t_json['password'] != password:
				raise DataApiException(
					DataApiErrors.PASSWORD_MISMATCH)
			# Update classification in dict
			t_json['classification'] = classification
			# Dump to json format
			t_modified_data = str.encode(json.dumps(t_json))
			# Update zNode
			self.client.set(tournament_path, value=t_modified_data)
			# TODO: Update players
			
		except LockTimeout as e:
			raise DataApiException(DataApiErrors.LOCK_TIMEOUT)
		finally:
			lock.release()
		return True


	def get_tournament_list(self):
		"""Get a list of the available tournaments

		Returns a list containing the names of the tournaments, their
		ids and the amount of players in each tournament.

			data = [{
				'name' : <string>,
				'id' : <integer>,
				'players' : <integer>,
				}]

		"""
		data = []
		tournament_ids = self.client.get_children(self.path)
		for t_id in tournament_ids:
			t_data, t_stats = self.client.get("/".join([
				self.path, t_id]))
			t_json = json.loads(t_data.decode())

			t_info = dict()
			t_info['name'] = t_json['name']
			t_info['id'] = t_id.lstrip('/').lstrip('t')
			t_info['players'] = t_stats.children_count

			data.append(t_info)

		return data
