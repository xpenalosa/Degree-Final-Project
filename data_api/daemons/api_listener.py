import sys
import re

from multiprocessing.connection import Listener
from kazoo.client import KazooClient
from kazoo.client import KazooState

from data_api import DataAPI

class DataApiListener():

	def __init__(self, pipe_address, zoo_address):
		# Requests pipe
		self.listener = Listener(pipe_address)
		# Kazoo client
		self.kz_client = KazooClient(hosts=zoo_address)
		self.kz_client.start()
		# Requesting API
		self.__api = DataAPI(self.kz_client)
		# Flag to disconnect
		self.__keep_running = True


	def run(self):
		"""Run a daemon, accepting requests for the API.

		This daemon will run until stop() is called on the
		ApiListener instance.
		"""
		while self.__keep_running:
			new_c = self.listener.accept()
			# Check there is data to read
			if not new_c.poll(0.2):
				# Close after 0.2 seconds idle
				new_c.close()
				continue
			# Accept new connections
			c_data = new_c.recv()
			# Request api
			result = self.__parse_request(c_data)
			# Return result of operation
			new_c.send(result)
			# Close connection
			new_c.close()

		# Close socket
		self.listener.close()
		# End Kazoo connection
		self.kz_client.stop()
		self.kz_client.close()


	def stop(self):
		"""Stop further connections to this client."""
		self.__keep_running = False	


	def __parse_request(self, req):
		"""Parse an incoming request.

		Returns a dictionary containing the following items:
			res = {
				code : <integer>,
				data : <string, dict>
			}
		"""
		result = {'code' : 0, 'data' : ''}

		if self.kz_client.state is not KazooState.CONNECTED:
			result['code'] = -2
			result['data'] = "Server unavailable"
			return result

		if type(req) is not dict:
			result['code'] = -1
			result['data'] = "Invalid data format"
			return result

		try:
			result['data'] = self.__run_request(req)
		except Exception as e:
			result['code'] = -3
			result['data'] = str(e)

		return result


	def __run_request(self, req):
		result = ''
		op = req.get('operation', None)
		data = req.get('data', None)
		if op == "create":
			result = self.__api.create_tournament(
				name = data['name'],
				modality = data['modality'],
				password = data['password'],
				players = data['players']
			)
		elif op == "update":
			result = self.__api.update_tournament(
				tournament_id = data['id'],
				version = data['version'],
				classification = data['classification'],
				password = data['password']
			)
		elif op == "delete":
			result = self.__api.delete_tournament(
				tournament_id = data['id'],
				password = data['password']
			)
		elif op == "get":
			result = self.__api.get_tournament(
				tournament_id = data['id']
			)
		elif op == "get_list":
			result = self.__api.get_tournament_list()
		elif op == "status":
			result = {
				'status' : self.kz_client.state,
				'address' : self.kz_client.hosts
			}
		elif op == "setpath":
			new_path = data['path']
			# Match filesystem format "/path/to/some_where/else"
			if re.compile("/([\d\w_]+/?)*").match(new_path):
				self.__api.set_data_path(data['path'])
				result = data['path']
			else:
				raise Exception("Malformed path")
		elif op == "dummy":
			result = 'OK'
		else:
			raise Exception("Operation " + op + " is invalid.")
		return result


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Wrong argument count!")
		print("python3 {0} <socket_port> <zookeeper_ip:port>".format(
			sys.argv[0]))
	else:
		pipe_address = ("localhost", int(sys.argv[1]))
		zoo_address = sys.argv[2]
		listener = DataApiListener(pipe_address, zoo_address)
		listener.run()
