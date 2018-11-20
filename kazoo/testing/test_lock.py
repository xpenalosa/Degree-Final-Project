from kazoo.recipe.lock import Lock, ReadLock, WriteLock
from kazoo.exceptions import LockTimeout

from basetest import BaseTest

class LockTest(BaseTest):

	def __init__(self, client_1, client_2):
		self.client_1 = client_1
		self.client_2 = client_2
		self.testpath = "/test/lock"

		
	@BaseTest.make_test
	def test_no_lock(self):
		self.client_1.ensure_path(self.testpath)
		self.client_2.ensure_path(self.testpath)
		path = self.client_1.create(self.testpath + "/no_lock", b"Info")
		data, stats = self.client_1.get(path)
		assert data == b"Info", "Data mismatch for client_1"
		data, stats = self.client_2.get(path)
		assert data == b"Info", "Data mismatch for client_2"


	@BaseTest.make_test
	def test_dual_lock_single(self):
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(self.testpath + "/single", b"Info")
		lock = self.client_1.Lock(path, "client_1")
		lock_1_acquired = False
		with lock:
			lock_1_acquired = True
			assert True, "Lock not acquired but passed check"
			assert lock.contenders() is not None, "No contenders"
			data, stats = self.client_1.get(path)
			assert data == b"Info", "Data mismatch"
		assert lock_1_acquired == True, "Did not acquire lock"


	@BaseTest.make_test
	def test_dual_lock_and_get(self):	
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(self.testpath + "/block", b"Info")
		lock = self.client_1.Lock(path, "client_1")
		lock_1_acquired = False
		with lock:
			lock_1_acquired = True
			data, stats = self.client_2.get(path)
			assert data is not None, "Data is none"
			assert data == b"Info", "Data mismatch"
		assert lock_1_acquired == True, "Did not acquire lock"


	@BaseTest.make_test
	def test_dual_locks(self):
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(self.testpath + "/2_locks", b"Info")
		lock_1 = self.client_1.Lock(path, "client_1")
		lock_1_acquired = False
		with lock_1:
			lock_1_acquired = True
			lock_2 = self.client_2.Lock(path, "client_2")
			lock_2_acquired = False
			try:
				lock_2_acquired = lock_2.acquire(timeout=0.1)
			except LockTimeout:
				# Expected behaviour
				assert lock_2_acquired == False
			else:
				lock_2.cancel()
				assert False, "Did not throw LockTimeout"
		assert lock_1_acquired == True, "Did not acquire lock 1"


	@BaseTest.make_test
	def test_read_then_read(self):
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(self.testpath + "/r_locks", b"Info")
		lock_1 = self.client_1.ReadLock(path, "client_1")
		lock_1_acquired = False
		with lock_1:
			lock_1_acquired = True
			lock_2 = self.client_2.ReadLock(path, "client_2")
			lock_2_acquired = False
			with lock_2:
				lock_2_acquired = True
				data, stats = self.client_2.get(path)
				assert data == b"Info", "Data mismatch"
			assert lock_2_acquired == True, "Did not acquire lock 2"
		assert lock_1_acquired == True, "Did not acquire lock 1"


	@BaseTest.make_test
	def test_read_then_write(self):
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(
			self.testpath + "/rw_locks",
			b"Info")
		lock_1 = self.client_1.ReadLock(path, "client_1")
		lock_1_acquired = False
		with lock_1:
			lock_1_acquired = True
			lock_2 = self.client_2.WriteLock(path, "client_2")
			try:
				lock_2.acquire(timeout=0.1)
			except LockTimeout:
				pass
			else:
				assert False, "Lock 2 was acquired"
		assert lock_1_acquired == True, "Did not acquire lock 1"


	@BaseTest.make_test
	def test_write_then_read(self):
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(
			self.testpath + "/wr_locks",
			b"Info")
		lock_1 = self.client_1.WriteLock(path, "client_1")
		lock_1_acquired = False
		with lock_1:
			lock_1_acquired = True
			lock_2 = self.client_2.ReadLock(path, "client_2")
			lock_2_acquired = False
			try:
				lock_2_acquired = lock_2.acquire(timeout=0.1)
			except LockTimeout:
				# Expected behaviour
				pass
			else:
				assert False, "Lock 2 was acquired"
			assert lock_2_acquired == False, "Acquired lock 2"
		assert lock_1_acquired == True, "Did not acquire lock 1"


	@BaseTest.make_test
	def test_write_then_write(self):	
		self.client_1.ensure_path(self.testpath)
		path = self.client_1.create(self.testpath + "/w_locks", b"Info")
		lock_1 = self.client_1.WriteLock(path, "client_1")
		lock_1_acquired = False
		with lock_1:
			lock_1_acquired = True
			lock_2 = self.client_2.WriteLock(path, "client_2")
			lock_2_acquired = False
			try:
				lock_2_acquired = lock_2.acquire(timeout=0.1)
			except LockTimeout:
				# Expected behaviour
				pass
			else:
				assert False, "Lock 2 was acquired"
			assert lock_2_acquired == False, "Acquired lock 2"
		assert lock_1_acquired == True, "Did not acquire lock 1"

