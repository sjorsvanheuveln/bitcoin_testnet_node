''' Example Code '''
from helpers import *
from network import *
from block import *
from ecc import PrivateKey
from script import p2pkh_script, Script, secret_script
from tx import TxIn, TxOut, Tx, TxFetcher
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
    bf = BloomFilter(size=5, function_count=2, tweak=90215)
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

    while len(found) < 3:
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


def send_opreturn_tx():
    raise NotImplementedError('make it')


def len_sassaman_pretty():
    len_sassamen_tx = '930a2114cdaa86e1fac46d15c74e81c09eee1d4150ff9d48e76cb0697d8e1d72'
    tx = TxFetcher.fetch(len_sassamen_tx)

    outs = tx.tx_outs
    #make 58 an empty line and pad it to the third comlumn
    outs[58].script_pubkey.cmds[2] = b'\x00'
    outs.append(outs[58])
    outs.append(outs[58])
    outs.pop(58)
    outs.pop(0)
    
    padding = 3

    print(padding * '\n')
    for i in range(0, int(len(outs) / 3)):
        line = padding * '   '

        for j in range(3):
            line += outs[i + j*26].script_pubkey.cmds[2].decode('utf-8') + ' '

        print(line)

    print(padding * '\n')

def len_sassaman():
    len_sassamen_tx = '930a2114cdaa86e1fac46d15c74e81c09eee1d4150ff9d48e76cb0697d8e1d72'
    tx = TxFetcher.fetch(len_sassamen_tx)
    outs = tx.tx_outs

    outs.pop(58)
    outs.pop(0)

    for out in outs:
        print(out.script_pubkey.cmds[2].decode('utf-8'))

def transaction_verification():
    pubkey = bytes.fromhex('038707dbb5b851f7952e4451ee38859601d3937d0c9260cc3d376f145d425ebea9')
    print('\nraw pubkey:', pubkey)
    h160 = hash160(pubkey)
    print('h160 pubkey:', h160.hex())
    extended_pubkey = b'\x6f' + h160 #test-prefix p2pkh

    address = encode_base58_checksum(extended_pubkey)
    print('base58 address:', address)

def endian_swap(s = '9b94830000000000'):
    '''hex string to little endian'''
    swaps = ''
    for i in range(0, len(s), 2):
        swaps += s[i+1] + s[i]
    print(swaps[::-1])

def art_from_chain(txid, testnet=True):
    '''Script for printing OP_RETURN art. Only parse OP_RETURN fields and concatenate.'''
    #rick astley and saylor proof

    tx = TxFetcher.fetch(txid, testnet)
    m = b''
    for out in tx.tx_outs:
        if out.script_pubkey.cmds[0] == 106:
            m += out.script_pubkey.cmds[1]
    print(m.decode('utf-8'), '\n')



