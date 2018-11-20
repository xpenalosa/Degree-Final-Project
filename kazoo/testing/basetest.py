from __future__ import print_function

import sys
import inspect

from functools import wraps

# Output coloring
from colorama import init as colorama_init
from colorama import Fore, Style
colorama_init(autoreset=True)


class BaseTest():

	@staticmethod
	def print_fail(text, msg):
	        print('\t{2}FAILED{3} {0}\n\t{2}{1}'.format(
				text,
				msg,
				Fore.RED + Style.BRIGHT,
				Style.RESET_ALL))

	@staticmethod
	def print_pass(text):
	        print('\t{1}PASSED{2} {0}'.format(
				text,
				Fore.GREEN + Style.BRIGHT,
				Style.RESET_ALL))

	@staticmethod
	def make_test(func):
		@wraps(func)
		def test_func(self):
			try:
				func(self)
			except:
				BaseTest.print_fail(func.__name__, sys.exc_info())
				return False
			else:
				BaseTest.print_pass(func.__name__)
				return True
		return test_func

	
	def run_tests(self, test_instance):
		print("Launching tests for class {1}{0}".format(
				test_instance.__class__.__name__,
				Fore.YELLOW + Style.BRIGHT))
		passed, failed = 0, 0

		methods = inspect.getmembers(
			test_instance,
			predicate=inspect.ismethod)
	        tests = [m[1] for m in methods if m[0][:5] == "test_"]
	        for t in tests:
			ret = t()
			if ret:
				passed += 1
			else:
				failed += 1
		return (passed, failed)
