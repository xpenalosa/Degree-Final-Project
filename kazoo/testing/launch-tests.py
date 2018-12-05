from __future__ import print_function

import datetime
import logging
import inspect
from kazoo.client import KazooClient

from colorama import init as colorama_init
from colorama import Fore, Style

from test_znode_instancing import ZNodeInstancingTest
from test_znode_data import ZNodeDataTest
from test_connection import ConnectionTest
from test_lock import LockTest
from test_api import ApiTest

def print_separator(text):
	print("="*40)
	print(" "*(20-len(text)//2) + text)
	print("="*40)


def run_tests(test_class_instances):
	"""Calls run_tests in the argument instances.
	
	Returns a list with the following format:
	    [
		Number of classes tested,
		( Number of tests passed, Number tests failed )
		( Testing start time, Testing finish time )
	    ]	
	"""
	# Init variables
	tested_classes, tests_passed, tests_failed = 0, 0, 0

	init_time = datetime.datetime.now()

	for test_instance in test_class_instances:
		tested_classes += 1
		passed, failed = test_instance.run_tests(test_instance)
		tests_passed += passed
		tests_failed += failed
		print()

	# Remove last print
	print('\033[1A',end='')

	end_time = datetime.datetime.now()

	return [tested_classes,
		(tests_passed, tests_failed),
		(init_time, end_time)]


def print_stats(stats):
	"""Prints the test statistics.

	The argument must be a list with the following format
	    [
		Number of classes tested,
		( Number of tests passed, Number tests failed )
		( Testing start time, Testing finish time )
	    ]	

	Example:
	>>> t1 = datetime.datetime.now()
	>>> keep_busy_for_10s()
	>>> t2 = datetime.datetime.now()
	>>> stats = [
	...	10,
	...	(23, 5),
	...	(t1, t2)]
	>>> print_stats(stats)
	=======================================
	             Tests finished!
	=======================================
	CLASSES TESTED 10
	TOTAL TESTS 28
		Passed 23
		Failed 5
	TIME SPENT
		0.0m 10.00s
	"""
	# Unpack stats
	tested_classes, test_results, times = stats

	# Test results
	tests_passed, tests_failed = test_results

	# Time stats
	start_time, end_time = times
	tdiff = end_time - start_time
	tdiff_s = tdiff.total_seconds() % 60
	tdiff_m = tdiff.total_seconds() // 60

	print_separator("Tests finished!")
	print("CLASSES TESTED {0}".format(tested_classes))
	print("TOTAL TESTS {0}".format(tests_passed + tests_failed))
	print("\t{1}Passed {0}".format(
		tests_passed,
		Fore.GREEN + Style.BRIGHT))
	print("\t{1}Failed {0}".format(
		tests_failed,
		Fore.RED + Style.BRIGHT))
	print("TIME SPENT")
	print("\t{0:2.0f}m {1:2.2f}s".format(tdiff_m, tdiff_s))



def create_tests(client_1, client_2):
	"""Instances all the classes to test.

	All the instanced classes should extend BaseTest (basetest.py).
	Returns a list of the instanced classes.
	"""
	t1 = ZNodeInstancingTest(client_1)
	t2 = ZNodeDataTest(client_1)
	t3 = LockTest(client_1, client_2)
	t4 = ApiTest(client_1, client_2)
	
	test_class_instances = [t1,t2,t3,t4,]
	return test_class_instances


def clean_tests(client):
	"""Deletes the testing node from the database."""
	client.delete("/test", recursive=True)


def run():
	"""Create the client and launch the tests.
	
	This function creates the Kazoo Client, connects it to the ZooKeeper
	ensemble and runs several tests. The tests to run are defined in the
	classes that extend BaseTest and are instanced in the method
	'create_tests'.

	The statistics for each class and test are printed to the console and
	the whole values are summarized at the end of the testing.

	After that, the client closes the connection to the ensemble and all
	the resources are freed.
	"""
	hosts = ','.join([
		"127.0.0.1:2181",
		"192.168.1.15:2181",
		"192.168.1.16:2181"])

	# Create clients
	zk = KazooClient(hosts=hosts)
	zk2 = KazooClient(hosts=hosts)

	# Connect to cluster
	zk.start()
	zk2.start()

	# Remove leftover test data
	clean_tests(zk)

	# Run tests
	test_class_instances = create_tests(zk, zk2)
	stats = run_tests(test_class_instances)
	# Print test statistics
	print_stats(stats)

	# Clean up test structure
	clean_tests(zk)
	# Stop clients
	zk.stop()
	zk2.stop()
	# Close connections and free resources
	zk.close()
	zk2.close()


def test_connection():
	"""Verify we can actually connect to the ensemble."""
	c_test = ConnectionTest()
	passed, failed = c_test.run_tests(c_test)
	return failed == 0


if __name__ == "__main__":
	logging.basicConfig()
	colorama_init(autoreset=True)

	print_separator("VERIFYING CONNECTION")
	if test_connection():
		print_separator("TESTING STARTS")
		run()




