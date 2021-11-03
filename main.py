#!/usr/bin/env python3

'''
Little Bitcoin Testnet Node project to write my first transaction (+more).
Author: Sjors van Heuveln 03-11-2021
'''

from helpers import *
from network import *
from block import *

'''params'''
host = 'testnet.programmingbitcoin.com'
port = 18333

node = SimpleNode(host, testnet=True, logging=True)
node.handshake()

'''get addresses'''
# node.getAddressesFromHost()

'''get headers'''
getheaders = GetHeadersMessage(start_block = testnet_genesis_block, end_block = testnet_block_3)
node.send(getheaders)
blocks = node.wait_for(HeadersMessage).blocks
print(blocks)

'''chech headers'''
for block in blocks:
  if block.check_pow():
    print('ok', block.hash().hex())

