''' Example Code '''
from helpers import *
from network import *
from block import *

def basic_node_action():
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