from __future__ import print_function

import logging
from kazoo.client import KazooClient

def print_node(client, nodename, depth):
	print('\t'*depth,end='')
	data,stats = client.get(nodename)
	print("{0}".format(nodename),end='')
	print("\t>>>\t\"{0}\"".format(data)) if data else print()
	if stats.children_count:
		childrenNames = client.get_children(nodename)
		for cname in childrenNames:
			print_node(client, nodename + "/" + cname, depth+1)

def print_tree(client):
	print("Displaying stored zNodes in tree structure")
	print_node(client, '', 0)


if __name__=='__main__':
	zk = KazooClient(hosts='127.0.0.1:2181')
	zk.start()
	print_tree(zk)
	zk.stop()
