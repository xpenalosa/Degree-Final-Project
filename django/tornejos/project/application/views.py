# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache

from .forms import CreateTournamentForm
from multiprocessing.connection import Client
import random

def __get_port(tried_ports):
	"""Get a listening port from the available list. """
	listed_ports = cache.get('ports')

	if not listed_ports:
		# Posts not in cache. Read from file
		client_ports = ''
		with open('/home/pi/tfg/scripts/listeners.cfg', 'r') as f:
			lines = f.readlines()

			start_port = int(lines[0].rstrip("\n"))

			zookeeper_clients = lines[1]
			client_count = len(zookeeper_clients.split(","))
			client_ports = range(start_port,start_port+client_count)

		listed_ports = ",".join([str(n) for n in list(client_ports)])
		cache.set('ports', listed_ports, None)
		
	# Filter tried ports
	available_ports = []
	for port in listed_ports.split(","):
		if port not in tried_ports:
			available_ports.append(port)
	# Select a random port
	if available_ports:
		return random.choice(available_ports)
	else:
		return None


def __send_req_to_api(data):
	tried_ports = []
	port = __get_port(tried_ports)

	while port is not None:
		address = ("localhost", int(port))
		result_data = ''
		try:
			client = Client(address)
			client.send(data)
			# Wait 0.75s for a response, or change server
			if client.poll(0.75):
				result_data = client.recv()
			client.close()
		except ConnectionRefusedError:
			# Client not available, try next
			pass	
		else:
			if result_data:
				code = result_data['code']		
				if code is not None and code != -1:
					# Connection to zookeeper OK
					return result_data
		
		# Connection failed, get new port
		tried_ports.append(port)
		port = __get_port(tried_ports)

	if port is None:
		return {'code': -1, 'data': "No nodes available"}
	


def create_tournament(request):
	"""
	if request.method == 'POST':
		#FIXME extract data from form
		#FIXME validate data
		req_create_data = {'operation' : 'create', 'data' : data}
		req_get_data = {'operation' : 'get', 'data' : identifier}
		context = __send_req_to_api(req_data)
		return render(request, "pages/display.html", context)
	else:
	"""
	form = CreateTournamentForm()
	context = {'form':form}
	return render(request, "pages/create.html", context=context)


def display_tournament(request, identifier):
	return render(request, "pages/list.html")
	req_data = {'operation' : 'get', 'data' : identifier}
	context = __send_req_to_api(req_data)
	"""
	context = {'data': {
		'name' : "T_Name",
		'players' : [
			{'name': 'P1', 'points' : 5, 'wins' : 2, 'losses' : 1, 'disqualified' : True},
			{'name': 'P2', 'points' : 6, 'wins' : 4, 'losses' : 0, 'disqualified' : False},
			{'name': 'P3', 'points' : 7, 'wins' : 6, 'losses' : 0, 'disqualified' : False}
		],
	}}
	"""
	return render(request, "pages/display.html", context)


def list_tournaments(request):
	req_data = {'operation' : 'get_list'}
	context = __send_req_to_api(req_data)
	print(context)
	return render(request, "pages/list.html", context)


def test(request):
	context = {'data': [{'name':'test', 'players':5, 'id':200}]}
	return render(request, "pages/list.html", context)
