from basetest import BaseTest
from sys import getsizeof
from kazoo.exceptions import ZookeeperError, BadVersionError

class ZNodeDataTest(BaseTest):
	"""Tests related to zNode data management

        These tests cover the management of data stored in zNodes and
	its versioning.
        """ 
	
	def __init__(self, client):
		self.client = client
		self.testpath = "/test/znode_data"


	@BaseTest.make_test
	def test_data_storage(self):
		"""Covered in zNode instantiation tests."""
		pass

	@BaseTest.make_test
	def test_data_storage_bytestring(self):	
		"""Verify we can store data after converting to bytestring."""
		self.client.ensure_path(self.testpath)
		bstring = "Data".encode()
		path = self.client.create(self.testpath + "/store_bts", bstring)
		assert path == self.testpath + "/store_bts"


	@BaseTest.make_test
	def test_data_access(self):
		"""Verify we can access stored data."""
		self.client.ensure_path(self.testpath)
		# Create node
		path = self.client.create(self.testpath + "/access", b"Data")
		# Get node
		data, stats = self.client.get(path)
		# Assert same data
		assert data is not None, "Data is None"
		assert data == b"Data", "Data is not b'Data'"
		assert data.decode('utf-8') == "Data", "Decoded data mismatch"


	@BaseTest.make_test
	def test_data_update(self):
		"""Verify the zNode data can be updated."""
		self.client.ensure_path(self.testpath)
		# Define data for both nodes
		init_bytestring = "Start".encode()
		end_bytestring = "End".encode()
		# Create node with initial data
		path = self.client.create(
			self.testpath + "/update",
			init_bytestring)
		# Retrieve data
		data, stats = self.client.get(path)
		# Verify stored data
		assert data is not None, "Initial data is None"
		assert data == init_bytestring, "Initial data mismatch"
		# Set new data
		stats = self.client.set(path, end_bytestring)
		data, stats = self.client.get(path)
		# Assert updated data
		assert data is not None, "End data is None"
		assert data != init_bytestring, "End data matches init data"
		assert data == end_bytestring, "End data mismatch"


	@BaseTest.make_test
	def test_data_update_version(self):
		"""Verify zNode version gets updated."""
		self.client.ensure_path(self.testpath)
		# Define data for both nodes
		init_bytestring = "Start".encode()
		end_bytestring = "End".encode()
		# Create node with initial data
		path = self.client.create(
			self.testpath + "/update_version",
			init_bytestring)
		# Retrieve data
		_, stats_before = self.client.get(path)
		assert stats_before is not None, "Stats before update is None"

		# Update node data
		self.client.set(path, end_bytestring)
		# Retrieve data
		_, stats_after = self.client.get(path)
		# Verify version update
		assert stats_after is not None, "Stats after update is None"
		assert stats_before.version != stats_after.version, ''.join([
			"Same version after update"])


	@BaseTest.make_test
	def test_data_update_version_restriction(self):
		"""Verify version locks data updates."""
		self.client.ensure_path(self.testpath)
		# Define data for both nodes
		init_bytestring = "Start".encode()
		end_bytestring = "End".encode()
		# Create node with initial data
		path = self.client.create(
			self.testpath + "/update_restrict",
			init_bytestring)
		# Retrieve data
		_, stats = self.client.get(path)
		# Force another node version
		new_version = stats.version + 1
		try:
			self.client.set(
				self.testpath + "/update_restrict",
				end_bytestring,
				version = new_version
				)
		except BadVersionError:
			# Expected behaviour
			pass
		else:
			raise AssertionError("zNode updated with bad version")
