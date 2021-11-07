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


def send_ascii_tx(message):
    '''fees might be an issue'''
    e = little_endian_to_int(hash256(PASSPHRASE))
    p = PrivateKey(e)
    #message = bytes.fromhex('2d2d2d2d2d2d2d2d2d204d49434841454c205341594c4f522054524942555445202d2d2d2d2d2d2d0a4040404040404040404040404040404040404040405152716a6f45445140404040404040404040400a40404040404040404040404040404040404025372720603b6a52552a4c414b6d44404040404040400a404040404040404040404040404040405872205f636b587a60602020272a665e2a212b6f514040400a4040404040404040404040404040423c605e5921272020202020202020203b585e4a692b254040400a404040404040404040404040403860213f5121606060696a6b55556d7327607a37275f6a514040400a404040404040404040404040406a3c2a59642e6060384040404040404040733b4a4a5e40405258400a404040404040404040404040402f4c7921547e207d404040404040404040407e51595140405738400a404040404040404040404040403e697c51777e6051404040404040404040516367714040404040400a40404040404040404040404040205e75517a607a40404040404040404040592663404040404040400a40404040404040404040404058202c3b4c7e206840255e60605e2f535740274160545152674e55400a4040404040404040404040407c5f60217e202075446021794c753b202020604e3b20273c7a7940400a404040404040404040404040697c206020207340782a3e6020272e20202053405820603b794440400a4040404040404040404040405220207e605e404040404051524e6b4b40524e4040264051404040400a4040404040404040404040406720274e3a71404040404040404040405151404040404051404040400a404040404040404040404040402c752c3b214040404040404040263a3740442b45514051405240400a40404040404040404040404040517c2c20374040404040406a2b20203b2c2c5f21697121402140400a4040404040404040404040404040407c60695140404040263d213a2c20206021696b517a407851400a4040404040404040404040404040406f4b6d40404040512c4e793b2c20605f2b72375376405140400a4040404040404040404040404040406145544051404058604e3827202e696a6d58456660574040400a404040404040404040404040404040675325277e3b693b37457c2020205f3a27603a6f447a4040400a4040404040404040404040404040404051407a20606269274545717e20203b6951413c55574040400a404040404040404040404040404040406752513b7e202c2a66556a51693c6a797d516b40404040400a404040404040404040404040424b5140516b2638687a3a2060214251516d672551415540404040400a40404040404040404040253b2020202c6e51514058524b7d4c7d694e4e446f7a78404040404040400a4040404040404040717e20202020202020203d5240516d695a5862514040404040404040404040400a4040404040407d27202020202020202020202020274c4b516d6a36514040404040404040404040400a404040442b20202020202020202020202020202020202060214a4e5140404051407a7140404040400a40407e20202020202020202020202020202020202020202020202020272c2c2e602020276f4040400a405920202020202020202020202020202020202020202020202020202020202020202020206077400a582020202020202020202020202020234745544f46465a45524f202020202020202020202e3a204a0a')
    msg_chunks = chop_OP_RETURN_message(message)

    #txin
    tx_in = TxFetcher.max_utxo_fetch(address = PUBKEY)


    outputs = []
    '''hand shake and get min fee'''
    node = SimpleNode(TESTNET_HOST2, testnet=True, logging=True)
    node.handshake()
    node.send(GenericMessage(b'feefilter', b''))
    min_fee = node.wait_for(FeefilterMessage).fee * len(msg_chunks)

    #opreturn output
    for msg in msg_chunks:
        payload_amount = 0
        payload_script = secret_script(msg)
        outputs.append(TxOut(amount=payload_amount, script_pubkey=payload_script))


    #change output
    change_amount = int(tx_in.amount - min_fee)
    change_h160 = p.point.hash160()
    change_script = p2pkh_script(change_h160)
    outputs.append(TxOut(amount=change_amount, script_pubkey=change_script))


    #create transaction, sign and send
    tx_obj = Tx(1, [tx_in], outputs, locktime = 0, testnet = True)
    tx_obj.sign_input(0, p)
    node.send(tx_obj)

    print('wait for msg')
    node.wait_for(FeefilterMessage)

def send_simple_tx(target_address):
    e = little_endian_to_int(hash256(PASSPHRASE))
    p = PrivateKey(e)
    tx_in = TxFetcher.max_utxo_fetch(address = PUBKEY)

    '''hand shake and get min fee'''
    node = SimpleNode(TESTNET_HOST2, testnet=True, logging=True)
    node.handshake()
    node.send(GenericMessage(b'feefilter', b''))
    min_fee = node.wait_for(FeefilterMessage).fee

    outputs = []
    #target output
    target_amount = int(100)
    target_h160 = decode_base58(target_address)
    target_script = p2pkh_script(target_h160)
    outputs.append(TxOut(amount=target_amount, script_pubkey=target_script))

    #change output
    change_amount = int(tx_in.amount - target_amount - min_fee)
    change_h160 = p.point.hash160()
    change_script = p2pkh_script(change_h160)
    outputs.append(TxOut(amount=change_amount, script_pubkey=change_script))

    #create transaction, sign and send
    tx_obj = Tx(1, [tx_in], outputs, locktime = 0, testnet = True)
    tx_obj.sign_input(0, p)
    node.send(tx_obj)

    print('wait for msg')
    node.wait_for(FeefilterMessage)


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



