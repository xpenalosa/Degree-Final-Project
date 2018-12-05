from __future__ import print_function
import sys
import os
import json

from basetest import BaseTest

# Add parent directory to path for data_api import
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import data_api


class ApiTest(BaseTest):
	
	def __init__(self, client_1, client_2):
		self.client_1 = client_1
		self.client_2 = client_2

		self.testpath = "/test/api"

		self.api = data_api.DataAPI(self.client_1)
		# Override data path
		self.api.path = self.testpath


	@BaseTest.make_test
	def test_create_tournament(self):
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
		data_json = json.loads(data)
		j_name = data_json['name']
		assert j_name == b"Tournament test", "Name " + j_name
		j_mod = data_json['modality']
		assert j_mod == 0, "Modality " + j_mod
		j_classif = data_json['classification']
		assert len(j_classif) == num_players - 1, ' '.join([
			"Number of players:", str(len(j_classif))])
		assert j_classif == u"UUUU", "Classification " + j_classif
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
			p_data_json = json.loads(p_data)
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










		
