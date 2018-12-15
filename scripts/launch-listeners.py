#!/usr/bin/python
import sys
import os
from subprocess import Popen

from data_api import DataApiListener

def run():
	start_port = 0
	zk_servers = ''

	# Read configuration from file
	with open('listeners.cfg', 'r') as f:
		start_port = int(f.readline().rstrip('\n'))
		# Servers and ports to connect to, comma-separated
		zk_servers = f.readline().rstrip('\n').split(',')

	for zk_server in zk_servers:
		print("Spawning process for server {0} at port {1}".format(
			zk_server,start_port))
		# Spawn a listener for each server
		Popen([
			"python3",
			"../data_api/daemons/api_listener.py",
			str(start_port),
			zk_server]
		)
		# Increment listener port
		start_port += 1
	

if __name__ == '__main__':
	run()
