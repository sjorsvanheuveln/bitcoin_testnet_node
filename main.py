#!/usr/bin/env python3

'''
Little Bitcoin Testnet Node project to write my first transaction (+more).
Author: Sjors van Heuveln 03-11-2021
'''

####################################
from examples import *
from helpers import *
from network import *

#basic_node_action(TESTNET_HOST2)
#send_transaction()
#getMempool(TESTNET_HOST2)
bloomfilter()
####################################

#print(0x51)

# hexdump = bytes.fromhex('81ccb4ee682bc1da3bda70176b7ccc616a6ba9da')
# print(hexdump.decode('ascii'))

# taproot = b'QhR?_q0{\x057#Q\xd4\xaf\x8b)\xa7\xa3\xc6\xe1\xc65\xf20\xf9\xa8N\x01\xdd\xa1\x15*'.hex()
# print(len(taproot), taproot)