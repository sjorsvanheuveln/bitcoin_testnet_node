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
####################################

node = SimpleNode(TESTNET_HOST, testnet=True, logging=True)
node.handshake()
node.send(MempoolMessage())
inv = node.wait_for(InvMessage)
print(inv)


# inv = node.wait_for(InvMessage)
# print(inv)




####################################

''' todo
    1.
'''