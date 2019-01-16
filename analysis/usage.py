from __future__ import print_function

import sys
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

def print_tree(client, host):
	print("Displaying stored zNodes in tree structure ({})".format(host))
	print_node(client, '', 0)


if __name__=='__main__':
	host = '127.0.0.1'
	port = '2181'
	if len(sys.argv) > 1:
		host = sys.argv[1]
	zk = KazooClient(hosts=':'.join([host, port]))
	zk.start()
	print_tree(zk, host)
	zk.stop()
