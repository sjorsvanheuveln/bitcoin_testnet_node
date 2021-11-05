''' Example Code '''
from helpers import *
from network import *
from block import *
from ecc import PrivateKey
from script import p2pkh_script, Script
from tx import TxIn, TxOut, Tx
from config import *
from merkleblock import MerkleBlock
from bloomfilter import *


def basic_node_action(host):
    '''Do so simple stuff:
        1. handshake
        2. getaddr
        3. ping/pong
        4. getheaders
        5. parse blocks
    '''

    '''setup node'''
    node = SimpleNode(host, testnet=True, logging=True)
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

def send_transaction(host):
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

    node = SimpleNode(host, testnet=True, logging=True)
    node.handshake()
    node.send(tx_obj)

def getMempool(host):
    node = SimpleNode(host, testnet=True, logging=True)
    node.handshake()
    node.send(MempoolMessage())
    inv = node.wait_for(InvMessage)
    print(inv)

def bloomfilter():
    address = PUBKEY
    h160 = decode_base58(address)
    bf = BloomFilter(size=10, function_count=1, tweak=90210)
    bf.add(h160)

    node = SimpleNode(TESTNET_HOST3, testnet=True, logging=True)
    node.handshake()
    node.send(GenericMessage(b'filterclear', b''))
    time.sleep(1)
    node.send(bf.filterload())

    headers = node.getHeadersFromBlock(START_BLOCK) #, END_BLOCK2

    getdata = GetDataMessage()
    for b in headers:
        if not b.check_pow():
            raise RuntimeError('proof of work is invalid')
        getdata.add_data(FILTERED_BLOCK_DATA_TYPE, b.hash())
    node.send(getdata)

    found = []
    merkle_count = 0
    secrets = []

    while not found:
        message = node.wait_for(MerkleBlock, Tx)
        if message.command == b'merkleblock':
            merkle_count += 1
            if not message.is_valid():
                raise RuntimeError('invalid merkle proof')
        else:
            print('\nTx incoming')
            for i, tx_out in enumerate(message.tx_outs):
                print('ID:', message.id(), ':', i)

                #OP_RETURN secrets
                if tx_out.script_pubkey.cmds[0] == 106:    
                    secrets.append(decode_opreturn_secret(tx_out.script_pubkey.cmds[1]))

                elif tx_out.script_pubkey.address(testnet=True) == address:
                    print('FOUND: {}:{}'.format(message.id(), i))
                    found.append(message.id())

    print('merkle_count:', merkle_count)
    print('secrets', secrets)

