from basetest import BaseTest

from kazoo.client import KazooClient

class ConnectionTest(BaseTest):
	"""Tests for connections.
	
	This class tests the different connection states and operations used by
	the Kazoo Client when connecting to the ZooKeeper ensemble.
	"""
	
	def __init__(self):
		"""Creates the KazooClient instance used for testing."""
		self.client = KazooClient(hosts=','.join([
			'127.0.0.1:2181',
			'192.168.1.15:2181',
			'192.168.1.16:2181']))


	@BaseTest.make_test
	def test_client_connection(self):
		"""Tests the connection to the ZooKeeper ensemble.
		
		Initiates the connection to the ensemble with a timeout of 5
		seconds. If the connection has not been established by then, a
		kazoo.interfaces.IHandler.timeout_exception is raised.
		
		The connection is verified and stopped. Then, the connection
		state is verified again (as not connected).
		"""
		# Can raise kazoo.interfaces.IHandler.timeout_error
		self.client.start(timeout=5)
		assert self.client.connected, "Client is not connected"
		self.client.stop()
		self.client.close()
		assert not self.client.connected, ' '.join([
			"Client is still connected",
			"after requesting connection stop"])
	
