import sys
import os
import json
import re
from multiprocessing.connection import Client

from kazoo.exceptions import NoNodeError

from basetest import BaseTest
from data_api import DataApiListener


class ApiListenerTest(BaseTest):
	
	def __init__(self, client):
		self.testpath = "/test/api_listener"
		self.client = client
		self.pipe_address = ("localhost", 6000)
		# Set testing path
		client = self.__create_api_client()
		client.send({'operation':'setpath','path':self.testpath})
		client.recv()
		client.close()


	def __del__(self):
		# Send one last message to exit blocking call
		client = self.__create_api_client()
		client.send({'operation' : "dummy"})
		if client.poll(0.1):
			client.recv()
		client.close()


	def __create_api_client(self):
		return Client(self.pipe_address)


	@BaseTest.make_test
	def test_create_tournament(self):
		"""Creates a tournament and verifies the stored information."""
		num_children = 5

		sent_data = dict()
		sent_data['operation'] = "create"
		sent_data['name'] = "Test tournament listener"
		sent_data['modality'] = 0
		sent_data['password'] = "test"
		sent_data['players'] = [str(n) for n in range(num_children)]

		api_client = self.__create_api_client()
		api_client.send(sent_data)
		if not api_client.poll(5):
			assert False, "No data returned."

		answer = api_client.recv()
		api_client.close()

		assert answer is not None, "Returned answer is None."
		assert type(answer) is dict, "Returned answer is not a dict."
		assert answer['code'] == 0, "Code mismatch " + str(answer)

		t_path = answer['data']
		assert type(t_path) is str, " ".join([
			"Data type mismatch", answer])
		t_path_rgx = re.compile("/([\d\w_]+/?)*")
		assert t_path_rgx.match(t_path) is not None, " ".join([
			"Data is not a path", t_path])

		# Verify the tournament exists
		data, stats = self.client.get(t_path)

		assert data is not None, "Node data is None"
		data_json = json.loads(data.decode())
		j_name = data_json['name']
		assert j_name == sent_data['name'], "Name " + j_name
		j_mod = data_json['modality']
		assert j_mod == sent_data['modality'], "Modality " + j_mod
		j_classif = data_json['classification']
		assert len(j_classif) == num_children - 1, ' '.join([
			"Number of players:", str(len(j_classif))])
		assert j_classif == "UUUU", "Classification " + j_classif
		assert stats.children_count == num_children, ' '.join([
			"Number of children zNodes", stats.children_count])

		# Players asserts
		player_nodes = self.client.get_children(t_path)
		# Reverse player list since kazoo returns reverse sorted list
		player_nodes = player_nodes[::-1]
		index = 0
		for p_node in player_nodes:

			p_data, p_stats = self.client.get(t_path + "/"
				+ p_node)

			assert p_data is not None
			p_data_json = json.loads(p_data.decode())
			# name, points, disqualified, wins, losses
			p_name = p_data_json['name']
			assert p_name == sent_data['players'][index], ' '.join(
				["Player", str(index), "name", p_name])
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
		num_children = 5

		sent_data = dict()
		sent_data['operation'] = "create"
		sent_data['name'] = "Test tournament listener 2"
		sent_data['modality'] = 0
		sent_data['password'] = "test"
		sent_data['players'] = [str(n) for n in range(num_children)]

		api_client = self.__create_api_client()
		api_client.send(sent_data)
		if not api_client.poll(5):
			assert False, "No data returned on create"

		answer = api_client.recv()
		api_client.close()
		
		t_path = answer['data']

		sent_data2 = dict()
		sent_data2['operation'] = "get"
		sent_data2['id'] = t_path.split('/')[-1].lstrip('t')

		api_client2 = self.__create_api_client()
		api_client2.send(sent_data2)
		if not api_client2.poll(5):
			assert False, "No data returned on get"
		answer2 = api_client2.recv()
		api_client2.close()
		
		assert answer2 is not None, "Returned answer2 is None."
		assert type(answer2) is dict, "Returned answer2 is not a dict."
		assert answer2['code'] == 0, "Code2 mismatch " + str(answer2)

		t_info = answer2['data']
		assert t_info is not None, "Answer2 data is None"

		o_name = t_info['name']
		assert o_name is not None, "Tournament name is None"
		assert o_name == sent_data['name'], " ".join([
			"Wrong tournament name", o_name])
		
		o_classif = t_info['classification']
		assert len(o_classif) == num_children - 1, " ".join([
			"Classification size", str(len(o_classif))])
		assert o_classif == "U"*(num_children-1), " ".join([
			"Classification value", o_classif])
		
		o_mod = t_info['modality']
		assert o_mod == sent_data['modality'], " ".join([
			"Wrong modality", str(o_mod)])

		o_version = t_info['version']
		assert o_version is not None, "Version is None"
		assert o_version == 0, "Version mismatch" + o_version

		o_players = t_info['players']
		assert o_players is not None, "Players array is None"
		assert len(o_players) == num_children, " ".join([
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

		# ---------- CREATE ----------

		num_children = 5

		sent_data = dict()
		sent_data['operation'] = "create"
		sent_data['name'] = "Test tournament listener 3"
		sent_data['modality'] = 0
		sent_data['password'] = "test"
		sent_data['players'] = [str(n) for n in range(num_children)]

		api_client = self.__create_api_client()
		api_client.send(sent_data)
		if not api_client.poll(5):
			assert False, "No data returned."

		answer = api_client.recv()
		api_client.close()

		t_path = answer['data']
		t_id = t_path.split('/')[-1].lstrip('t')

		# ---------- DELETE ----------

		sent_data3 = dict()
		sent_data3['operation'] = "delete"
		sent_data3['id'] = t_id
		sent_data3['password'] = sent_data['password']

		api_client3 = self.__create_api_client()
		api_client3.send(sent_data3)
		if not(api_client3.poll(5)):
			assert False, "No data returned on delete"
		answer3 = api_client3.recv()
		api_client3.close()

		assert type(answer3) is dict, " ".join([
			"Returned answer3 is not a dict", str(answer3)])
		assert answer3['code'] == 0, "Code3 mismatch " + str(answer3)

		del_data = answer3['data']
		assert del_data == 0, "Data3 mismatch " + del_data

		try:
			data, stats = self.client.get(t_path)
		except NoNodeError:
			# Expected behaviour
			pass
		else:
			assert False, "No exception raised on client.get"
		
	
	@BaseTest.make_test
	def test_update_tournament(self):
		"""Creates and updates a tournament.

		Creates the zNodes corresponding to a tournament and updates
		the classification of the players by calling the API. It is
		verified that the classification has been updated by requesting
		the tournament with another API call.
		"""
		# ---------- CREATE ----------

		num_children = 5

		sent_data = dict()
		sent_data['operation'] = "create"
		sent_data['name'] = "Test tournament listener 3"
		sent_data['modality'] = 0
		sent_data['password'] = "test"
		sent_data['players'] = [str(n) for n in range(num_children)]

		api_client = self.__create_api_client()
		api_client.send(sent_data)
		if not api_client.poll(5):
			assert False, "No data returned."

		answer = api_client.recv()
		api_client.close()

		t_path = answer['data']

		# ---------- GET ----------

		t_id = t_path.split('/')[-1].lstrip('t')

		sent_data2 = dict()
		sent_data2['operation'] = "get"
		sent_data2['id'] = t_id

		api_client2 = self.__create_api_client()
		api_client2.send(sent_data2)
		if not api_client2.poll(5):
			assert False, "No data returned on get"
		answer2 = api_client2.recv()
		api_client2.close()

		t_info = answer2['data']

		# ---------- UPDATE ----------

		new_classif = t_info['classification']
		new_classif = "1" + new_classif[1:]

		sent_data3 = dict()
		sent_data3['operation'] = "update"
		sent_data3['id'] = t_id
		sent_data3['version'] = t_info['version']
		sent_data3['classification'] = new_classif
		sent_data3['password'] = sent_data['password']

		api_client3 = self.__create_api_client()
		api_client3.send(sent_data3)
		if not api_client3.poll(5):
			assert False, ""
		answer3 = api_client3.recv()
		api_client3.close()
	
		assert type(answer3) is dict, " ".join([
			"Returned answer3 is not a dict", str(answer3)])
		assert answer3['code'] == 0, "Code3 mismatch " + str(answer3)

		t_out = answer3['data']
		assert type(t_out) is bool, "Data3 is not a bool." + str(t_out)
		assert t_out, "Data3 is False"

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
		# ---------- CREATE ----------
		num_children = 5

		sent_data = dict()
		sent_data['operation'] = "create"
		sent_data['name'] = "Test tournament listener 4"
		sent_data['modality'] = 0
		sent_data['password'] = "test"
		sent_data['players'] = [str(n) for n in range(num_children)]

		api_client = self.__create_api_client()
		api_client.send(sent_data)
		if not api_client.poll(5):
			assert False, "No data returned."

		answer = api_client.recv()
		api_client.close()

		assert answer is not None, "Returned answer is None."
		assert type(answer) is dict, "Returned answer is not a dict."
		t_path = answer['data']
		t_id = t_path.split('/')[-1].lstrip('t')

		# ---------- GET LIST ----------

		sent_data2 = dict()
		sent_data2['operation'] = "get_list"
		
		api_client2 = self.__create_api_client()
		api_client2.send(sent_data2)
		if not api_client2.poll(5):
			assert False, "No data returned."

		answer2 = api_client2.recv()
		api_client2.close()

		assert answer2 is not None, "Returned answer2 is None."
		assert type(answer2) is dict, "Returned answer2 is not a dict."
		assert answer2['code'] == 0, "Code2 mismatch: " + str(answer2)

		t_infos = answer2['data']
		assert type(t_infos) is list, " ".join([
			"Data2 is not a list", str(t_infos)])
		assert len(t_infos) > 0, "Data2 is a list of length 0."

		# Verify the created tournament is in the list
		for t_info in t_infos:
			assert type(t_info) is dict, " ".join([
				"Tournament info is not a dict:",
				str(t_info)])
			t_name = t_info['name']
			assert t_name is not None, " ".join([
				"Name is None:", str(t_info)])

			# Check against original name
			if t_name != sent_data['name']:
				continue

			# Check player count
			t_players = t_info['players']
			assert t_players is not None, " ".join([
				"Player count is None",
				str(t_info)])
			assert t_players == num_children, " ".join([
				"Player count mismatch:",
				str(t_players),
				"/",
				str(num_children)])

			# Check tournament id matches the path created
			t_id_out = t_info['id']
			assert t_id_out is not None, " ".join([
				"Tournament id is None",
				str(t_info)])
			assert t_id_out == t_id, " ".join([
				"Tournament id mismatch",
				str(t_id_out),
				"/",
				str(t_id)])

			# Skip checks on other tournaments
			break


		
		





	
