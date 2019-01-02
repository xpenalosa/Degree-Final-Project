# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.contrib import messages
from django.contrib.messages import add_message

from multiprocessing.connection import Client
import sys
import random
import re
import math

from .forms import CreateTournamentForm, UpdateTournamentForm

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
	context = dict()
	if request.method == 'POST':
		form = CreateTournamentForm(request.POST)
		if form.is_valid():
			form_data = form.cleaned_data
			players = re.split(r"[\n,\s]+", form_data['players'])
			random.shuffle(players)
			req_create_data = {
				'operation' : 'create',
				'data' : {
					'name' : form_data['name'],
					'modality' : 0,
					'password' : form_data['pass1'],
					'players' : players
				}
			}
			answer = __send_req_to_api(req_create_data)
			if answer['code'] == 0:
				zNodeName = answer['data']
				identifier = zNodeName.split("/")[2].lstrip('t')

				req_get_data = {
					'operation' : 'get',
					'data' : identifier
				}
				context = __send_req_to_api(req_get_data)

				return HttpResponseRedirect("/t/{}/".format(
					int(identifier)))
			context['error'] = "Code {}, data {}".format(
				answer['code'], answer['data'])
	else:
		form = CreateTournamentForm()


	context['form'] = form
	return render(request, "pages/create.html", context=context)


def display_tournament(request, identifier):
	req_data = {
		'operation' : 'get',
		'data' : {
			'id' : str(identifier)
		}
	}
	context = __send_req_to_api(req_data)
	if context['code'] == 0:
		context['form'] = UpdateTournamentForm(initial={
			'version' : context['data']['version'],
			'classification' : context['data']['classification']
		})
		return render(request, "pages/display.html", context)
	else:
		return render(request, "pages/error.html", context)


def list_tournaments(request):
	req_data = {'operation' : 'get_list'}
	context = __send_req_to_api(req_data)
	if context['code'] == 0:
		return render(request, "pages/list.html", context)
	else:
		return render(request, "pages/error.html", context)


def test(request):
	context = {'data': [{'name':'test', 'players':5, 'id':200}]}
	return render(request, "pages/list.html", context)


def update_tournament(request, identifier):
	if request.method == "POST":
		form = UpdateTournamentForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			password = cleaned_data.get('password')
			new_classification = cleaned_data.get('classification')
			version = cleaned_data.get('version')
			req_data = {
				'operation' : 'update',
				'data' : {
					'id' : str(identifier),
					'password' : password, 
					'classification' : new_classification,
					'version' : version
				}
			}
			context = __send_req_to_api(req_data)
			if context['code'] == 0:
				messages.add_message(request, messages.INFO,
					"Informació actualitzada!")
			else:
				messages.add_message(request, messages.ERROR,
					context)
		else:
			messages.add_message(request, messages.ERROR,
				"")
	return redirect("/t/{}/".format(identifier))
	        

def delete_tournament(request, identifier):
	if request.method == "POST":
		form = UpdateTournamentForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			password = cleaned_data.get('password')
			req_data = {
				'operation' : 'delete',
				'data' : {
					'id' : str(identifier),
					'password' : password, 
				}
			}
			context = __send_req_to_api(req_data)
			if context['code'] == 0:
				messages.add_message(request, messages.INFO,
					"El torneig s'ha esborrat correctament")
				return redirect("/list")
			else:
				messages.add_message(request, messages.ERROR,
					context)
		else:
			messages.add_message(request, messages.ERROR,
				"Formulari invàlid")
	return redirect("/t/{}/".format(identifier))


