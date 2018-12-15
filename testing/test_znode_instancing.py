from __future__ import print_function

from basetest import BaseTest
from kazoo.exceptions import NodeExistsError, NoNodeError, NotEmptyError

class ZNodeInstancingTest(BaseTest):
	"""Tests related to zNode instancing.
	
	These tests cover the creation and deletion of zNodes in the ZooKeeper
	ensemble, as well as some special cases that should raise Errors.
	"""

	def __init__(self, client):
		self.client = client
		self.testpath = "/test/znode_instancing"


	@BaseTest.make_test
	def test_node_creation(self):
		"""Verify we can create a node.

		This test creates a zNode called '/node_creation' and verifies
		that the data is stored correctly.
		"""
		self.client.ensure_path(self.testpath)
		# Ensure node does not exist
		if self.client.exists(self.testpath + "/node_creation"):
			self.client.delete(self.testpath + "/node_creation")

		# Create node
		real_path = self.client.create(
			self.testpath + "/node_creation",
			b"test")
			
		# Validate node exists
		assert real_path is not None, "real_path is None"
		assert real_path == self.testpath + "/node_creation", ''.join([
			"real_path = {0}".format(real_path)])

		# Validate stored data
		data, stat = self.client.get(self.testpath + "/node_creation")
		assert data == b"test", "data = {0}".format(data)

	
	@BaseTest.make_test
	def test_node_deletion(self):
		"""Verify we can delete a node.

		This test creates a zNode called '/node_deletion' and deletes
		it. After that, it is verified that the zNode does no longer
		exist.
		"""
		self.client.ensure_path(self.testpath)

		path = self.client.create(
				self.testpath + "/node_deletion",
				b"test")
		
		self.client.delete(path)
		znode1 = self.client.exists(self.testpath + "/node_deletion")
		znode2 = self.client.exists(path)

		assert znode1 is None, "zNode from built path is not None"
		assert znode2 is None, "zNode from real path is not None"


	@BaseTest.make_test
	def test_node_creation_duplicate(self):
		"""Verify duplicate nodes can not exist.
		
		This test creates a zNode called '/duplicate_node' twice. The
		second call to create is expected to raise a NodeExistsError.
		"""
		self.client.ensure_path(self.testpath)
		path_original = self.client.create(
			self.testpath + "/duplicate_node",
			b'Original')
		path_duplicate = ''
		try:
			path_duplicate = self.client.create(
				path_original,
				b'Duplicate')
		except NodeExistsError as e:
			# Expected resolution
			pass
		else:
			raise AssertionError(' '.join([
				"Duplicate node has been created in",
				path2]))	
		

	@BaseTest.make_test
	def test_node_deletion_unexisting(self):
		"""Verify we can not delete unexisting nodes.

		This test makes sure a zNode called '/unexisting_zNode' does
		not exist by deleting it if necessary, and then tries to delete
		it again. The second call to delete is expected to raise a
		NoNodeError.
		"""
		self.client.ensure_path(self.testpath)
		znode = self.client.exists(self.testpath + "/unexisting_node")
		# Make sure node does not exist
		if znode is not None:
			self.client.delete(self.testpath + "/unexisting_node")
		# Try to delete
		try:
			self.client.delete(self.testpath + "/unexisting_node")
		except NoNodeError as e:
			# Expected resolution
			pass
		else:
			raise AssertionError(' '.join([
				"Unexisting node deleted",
				"without raising error"]))


	@BaseTest.make_test
	def test_node_creation_children(self):
		"""Verify nodes can not be created under non-existing paths.
		
		This test makes sure the path /empty does not exist by deleting
		if necessary and tries to create a node inside called
		'child_node'. The call to create is expected to raise a
		NoNodeError since the parent node(path) does not exist.
		"""
		self.client.ensure_path(self.testpath)
		znode = self.client.exists(self.testpath + "/empty")
		if znode is not None:
			self.client.delete(self.testpath + "/empty")

		try:
			path = self.client.create(
				self.testpath + "/empty/child_node",
				b"Child")
		except NoNodeError as e:
			# Expected resolution
			pass
		else:
			raise AssertionError(' '.join([
				"Child node has been created in non-existing",
				"path",
				self.testpath + "/empty/child_node"]))

	@BaseTest.make_test
	def test_node_deletion_children(self):
		"""Verify nodes can not be deleted if they have children.
		
		This test creates two nested nodes and tries to delete the
		parent node. The call to create is expected to raise a
		NotEmptyError since the parent has children and the argument
		'recursive' is not set to True.
		"""
		self.client.ensure_path(self.testpath)
		self.client.create(self.testpath + "/parent", b"Parent")
		self.client.create(self.testpath + "/parent/child", b"Child")

		try:
			znode = self.client.delete(self.testpath + "/parent")
		except NotEmptyError as e:
			# Expected behaviour
			pass
		else:
			raise AssertionError(' '.join([
				"Parent node has been deleted with existing",
				"children",]))


	@BaseTest.make_test
	def test_path_creation(self):
		"""Verify we can create a path."""
		self.client.ensure_path(self.testpath + "/path_creation")
		znode = self.client.exists(self.testpath + "/path_creation")

		# Returns status of the node, or None if it does not exist
		assert znode is not None, "zNode is None"	
	

	@BaseTest.make_test
	def test_path_deletion(self):
		"""Verify we can delete an existing path.

		The path is created before trying to delete it.
		"""
		self.client.ensure_path(self.testpath + "/path_deletion")
		self.client.delete(self.testpath + "/path_deletion")
		znode = self.client.exists(self.testpath + "/path_deletion")

		assert znode is None, ''.join([
			self.testpath,
			'/path_deletion still exists'])


	@BaseTest.make_test
	def test_path_creation_recursive(self):
		"""Verify we can create a path with multiple depth levels."""
		self.client.ensure_path(
			self.testpath + "/recursive/path_creation")
		znode = self.client.exists(
			self.testpath + "/recursive/path_creation")
		assert znode is not None, "Path was not created"

	
	@BaseTest.make_test
	def test_path_deletion_recursive(self):
		"""Verify we can delete a path recursively.

		The path is created before trying to delete it.
		"""
		self.client.ensure_path(
			self.testpath + "/recursive/path_deletion")
		self.client.delete(
			self.testpath + "/recursive/path_deletion",
			recursive=True)
		znode = self.client.exists(''.join([
				self.testpath,
				"/recursive/path_deletion"]))

		assert znode is None, ''.join([
			self.testpath,
			'/recursive/path_deletion still exists'])

