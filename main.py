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

#setup bloomfilter



# for b in headers:
#     print(b.check_pow(), b.hash().hex())



# ####################################

# ''' todo
#     1. Check out services. Apparently only 1037/1036 allow mempool messages.
# '''


# node.send(GenericMessage(b'getaddr',b''))
# addr = node.wait_for(AddressMessage)
# for a in addr.addr_list:
#     if a.services == 1037:
#         print(a)

