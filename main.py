#!/usr/bin/env python3

'''
Little Bitcoin Testnet Node project to write my first transaction (+more).
Author: Sjors van Heuveln 03-11-2021
'''

####################################
from examples import *
from helpers import *
from network import *

# basic_node_action()
# send_transaction()
getMempool()
####################################

node = SimpleNode(TESTNET_HOST, testnet=True, logging=True)
node.handshake()


####################################

''' todo
    1. Could work on these responses.
    receiving: sendheaders: 
    receiving: sendcmpct: 000200000000000000
    receiving: sendcmpct: 000100000000000000
'''