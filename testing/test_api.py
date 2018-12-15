import sys
import os
import json

from basetest import BaseTest

from kazoo.exceptions import NoNodeError

# Add parent directory to path for data_api import
from data_api import DataAPI


class ApiTest(BaseTest):
	
	def __init__(self, client_1, client_2):
		self.client_1 = client_1
		self.client_2 = client_2

		self.testpath = "/test/api"

		self.api = DataAPI(self.client_1)
		# Override data path
		self.api.path = self.testpath


	@BaseTest.make_test
	def test_create_tournament(self):
		"""Creates a tournament and verifies the stored information."""
		self.client_1.ensure_path(self.testpath)

		t_name = "Tournament test"
		t_modality = 0 # Irrelevant as of now
		t_password = "test"

		num_players = 5
		players = [str(n) for n in range(num_players)]
		
		# Create tournament
		t_path = self.api.create_tournament(t_name, t_modality,
			t_password, players)
		assert t_path is not None, "Created path is None"
		assert t_path == "/test/api/t0000000000", "Wrong path" + t_path

		# Retrieve information
		data, stats = self.client_1.get(t_path)

		# Tournament asserts
		assert data is not None
		data_json = json.loads(data.decode())
		j_name = data_json['name']
		assert j_name == "Tournament test", "Name " + j_name
		j_mod = data_json['modality']
		assert j_mod == 0, "Modality " + j_mod
		j_classif = data_json['classification']
		assert len(j_classif) == num_players - 1, ' '.join([
			"Number of players:", str(len(j_classif))])
		assert j_classif == "UUUU", "Classification " + j_classif
		assert stats.children_count == len(players), ' '.join([
			"Number of children zNodes", stats.children_count])
		
		# Players asserts
		player_nodes = self.client_1.get_children(t_path)
		# Reverse player list since kazoo returns reverse sorted list
		player_nodes = player_nodes[::-1]
		index = 0
		for p_node in player_nodes:

			p_data, p_stats = self.client_1.get(t_path + "/"
				+ p_node)

			assert p_data is not None
			p_data_json = json.loads(p_data.decode())
			# name, points, disqualified, wins, losses
			p_name = p_data_json['name']
			assert p_name == players[index], ' '.join([
				"Player", str(index), "name", p_name])
			p_points = p_data_json['points']
			assert p_points == 0, ' '.join([
				"Player", str(index), "points",
				str(p_points)])
			p_disq = p_data_json['disqualified']
			assert p_disq == False, ' '.join([
				"Player", str(index), "disqualified",
				str(p_disq)])
			p_wins = p_data_json['wins']
			assert p_wins == 0, ' '.join([
				"Player", str(index), "wins",
				str(p_wins)])
			p_losses = p_data_json['losses']
			assert p_losses == 0, ' '.join([
				"Player", str(index), "losses",
				str(p_losses)])

			# structure assert
			p_children = p_stats.children_count
			assert p_children == 0, ' '.join([
				"Player", str(index), "has",
				str(p_children), "children"])
			index += 1


	@BaseTest.make_test
	def test_get_tournament(self):
		"""Creates and retrieves the info of a tournament."""
		self.client_1.ensure_path(self.testpath)

		t_name = "Tournament test 2"
		t_modality = 0 # Irrelevant as of now
		t_password = "test"

		num_players = 5
		players = [str(n) for n in range(num_players)]
		
		# Create tournament
		t_path = self.api.create_tournament(t_name, t_modality,
			t_password, players)
		# Get zNode
		t_zNode_data, t_zNode_stats  = self.client_1.get(t_path)
		# Get tournament id from path
		t_id = t_path.split('/')[-1].lstrip('t')
		# Get information from tournament id
		t_info = self.api.get_tournament(t_id)
		assert t_info is not None, "API returned no information"
		
		o_name = t_info['name']
		assert o_name is not None, "Tournament name is None"
		assert o_name == t_name, "Wrong tournament name" + o_name
		
		o_classif = t_info['classification']
		assert len(o_classif) == num_players - 1, " ".join([
			"Classification size", str(len(o_classif))])
		assert o_classif == "U"*(num_players-1), " ".join([
			"Classification value", o_classif])
		
		o_mod = t_info['modality']
		assert o_mod == t_modality, "Wrong modality " + str(o_mod)

		o_version = t_info['version']
		assert o_version is not None, "Version is None"
		assert o_version == t_zNode_stats.version, "Version mismatch"

		o_players = t_info['players']
		assert o_players is not None, "Players array is None"
		assert len(o_players) == num_players, " ".join([
			"Wrong player count", str(len(o_players))])

		index = 0
		for p in o_players[::-1]:
			p_name = p['name']
			assert p_name == str(index), " ".join([
				"Player", str(index), "name", p_name])

			p_points = p['points']
			assert p_points == 0, " ".join([
				"Player", str(index), "points", str(p_points)])
			
			p_disq = p['disqualified']
			assert p_disq == False, " ".join([
				"Player", str(index), "disqualified", p_disq])

			p_wins = p['wins']
			assert p_wins == 0, " ".join([
				"Player", str(index), "wins", str(p_wins)])

			p_losses = p['losses']
			assert p_losses == 0, " ".join([
				"Player", str(index), "losses", str(p_losses)])

			index += 1


	@BaseTest.make_test
	def test_delete_tournament(self):
		"""Creates and deletes a tournament.

		Creates the zNodes corresponding to a tournament and deletes
		them by calling the API. It is verified that the nodes no
		longer exist after the call.
		"""
		self.client_1.ensure_path(self.testpath)

		t_name = "Tournament test 3"
		t_modality = 0 # Irrelevant as of now
		t_password = "test"

		num_players = 5
		players = [str(n) for n in range(num_players)]
		
		# Create tournament
		t_path = self.api.create_tournament(t_name, t_modality,
			t_password, players)
		# Get tournament id from path
		t_id = t_path.split('/')[-1].lstrip('t')
		
		result = self.api.delete_tournament(t_id, t_password)
		assert result == 0, "Wrong return value " + result
		
		try:
			data, stats = self.client_1.get(t_path)
		except NoNodeError:
			# Expected behaviour
			pass
		else:
			assert False, "Did not raise exception"
		
	
	@BaseTest.make_test
	def test_update_tournament(self):
		"""Creates and updates a tournament.

		Creates the zNodes corresponding to a tournament and updates
		the classification of the players by calling the API. It is
		verified that the classification has been updated by requesting
		the tournament with another API call.
		"""
		self.client_1.ensure_path(self.testpath)

		t_name = "Tournament test 4"
		t_modality = 0 # Irrelevant as of now
		t_password = "test"

		num_players = 5
		players = [str(n) for n in range(num_players)]
		
		# Create tournament
		t_path = self.api.create_tournament(t_name, t_modality,
			t_password, players)
		# Get tournament id from path
		t_id = t_path.split('/')[-1].lstrip('t')

		t_out = self.api.get_tournament(t_id)
		
		new_classif = t_out['classification']
		new_classif = self.api.MATCH_STATUS["P1_WON"] + new_classif[1:]
		result = self.api.update_tournament(t_id, t_out['version'],
			new_classif, t_password)
		assert result == True, "Wrong return value " + result

		t2_out = self.api.get_tournament(t_id)
		assert t_out['name'] == t2_out['name'], " ".join([
			"Name mismatch:", t_out['name'], "!=", t2_out['name']])	
		assert t_out['version'] != t2_out['version'], " ".join([
			"Same version:", t_out['version']])
		assert t2_out['classification'] == new_classif, " ".join([
			"Classification mismatch:", t_out['classification'],
			"!=", new_classif])
		# TODO: Test players when api is updated
		
		
	@BaseTest.make_test
	def test_get_tournament_list(self):
		"""Creates a tournament and gets a list of created tournaments.

		Creates the zNodes corresponding to a tournament and retrieves
		the list of created tournaments with a call to the API.
		Verifies that at least one tournament is created (more may be
		present, since the testing node is not deleted between tests)
		and matches the information returned in the API call with the
		information in each tournament.
		"""
		self.client_1.ensure_path(self.testpath)

		t_name = "Tournament test 5"
		t_modality = 0 # Irrelevant as of now
		t_password = "test"

		num_players = 5
		players = [str(n) for n in range(num_players)]
		
		# Create tournament
		t_path = self.api.create_tournament(t_name, t_modality,
			t_password, players)
		# Get tournament id from path
		t_id = t_path.split('/')[-1].lstrip('t')

		t_info_array = self.api.get_tournament_list()
		assert len(t_info_array) > 0, "No tournaments were returned"
		
		index = 0
		for t_info in t_info_array:
			t_info_id = t_info['id']
			assert t_info_id is not None, " ".join([
				"Tournament", index, "id is None"])
	
			t_info_t = self.api.get_tournament(t_info_id)

			t_info_name = t_info['name']
			assert t_info_name is not None, " ".join([
				"Tournament", index, "name is None"])
			assert t_info_name == t_info_t['name'], " ".join([
				"Tournament", index, "name mismatch",
				t_info_name, "!=", t_info_t['name']])

			t_info_pc = t_info['players']
			assert t_info_pc is not None, " ".join([
				"Tournament", index, "player count is None"])
			assert t_info_pc == len(t_info_t['players']), " ".join([
				"Tournament", index, "player count mismatch:",
				str(t_info_pc), "!=",
				str(len(t_info_t['players']))])

			index += 1
