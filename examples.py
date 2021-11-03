''' Example Code '''
from helpers import *
from network import *
from block import *
from ecc import PrivateKey
from script import p2pkh_script, Script
from tx import TxIn, TxOut, Tx
from config import PASSPHRASE

def basic_node_action():
    '''Do so simple stuff:
        1. handshake
        2. getaddr
        3. ping/pong
        4. getheaders
        5. parse blocks
    '''

    '''setup node'''
    node = SimpleNode(TESTNET_HOST, testnet=True, logging=True)
    node.handshake()

    '''get addresses'''
    '''uncomment to get addresses'''
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

def send_transaction():
    e = little_endian_to_int(hash256(PASSPHRASE))
    p = PrivateKey(e)
    a = p.point.address(compressed=True, testnet=True)
    #print('my pubkey:', a)

    prev_tx = bytes.fromhex('d1e7ad7065b9f2ea10207778fdf224f297915e091c993c4bbeeed4cfaba69661')
    prev_index = 0
    tx_in = TxIn(prev_tx, prev_index)

    #change output
    change_amount = int(96000)
    change_h160 = p.point.hash160()
    change_script = p2pkh_script(change_h160)
    change_output = TxOut(amount=change_amount, script_pubkey=change_script)

    #target output
    target_amount = int(900)
    target_h160 = decode_base58('mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt')
    target_script = p2pkh_script(target_h160)
    target_output = TxOut(amount=target_amount, script_pubkey=target_script)
    tx_obj = Tx(1, [tx_in], [change_output, target_output], locktime = 0, testnet = True)


    # sign the one input in the transaction object using the private key
    tx_obj.sign_input(0, p)
    # print the transaction's serialization in hex
    # print('\n', tx_obj.serialize().hex(), '\n')
    # broadcast at http://testnet.blockchain.info/pushtx

    node = SimpleNode(TESTNET_HOST, testnet=True, logging=True)
    node.handshake()
    node.send(tx_obj)

def getMempool():
    node = SimpleNode(TESTNET_HOST, testnet=True, logging=True)
    node.handshake()
    node.send(MempoolMessage())
    inv = node.wait_for(InvMessage)
    print(inv)
