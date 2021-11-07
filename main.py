#!/usr/bin/env python3

'''
Little Bitcoin Testnet Node project to write my first transaction (+more).
Author: Sjors van Heuveln 03-11-2021
'''

####################################
from examples import *
from helpers import *
from network import *
from config import *

#basic_node_action(TESTNET_HOST2)
#send_transaction()
#getMempool(TESTNET_HOST2)
#bloomfilter()
####################################


e = little_endian_to_int(hash256(PASSPHRASE))
p = PrivateKey(e)
a = p.point.address(compressed=True, testnet=True)


#txin
tx_in = TxFetcher.max_utxo_fetch(address = PUBKEY)


'''hand shake and get min fee'''
node = SimpleNode(TESTNET_HOST2, testnet=True, logging=True)
node.handshake()
node.send(GenericMessage(b'feefilter', b''))
min_fee = node.wait_for(FeefilterMessage).fee


#target output
target_amount = int(100)
target_h160 = decode_base58('mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt')
target_script = p2pkh_script(target_h160)
target_output = TxOut(amount=target_amount, script_pubkey=target_script)

#opreturn output
secret_amount = int(0)
secret_payload = bytes('hello world', 'ascii')
secret_script = secret_script(secret_payload)
secret_output = TxOut(amount=secret_amount, script_pubkey=secret_script)

#change output
change_amount = int(tx_in.amount - target_amount - min_fee)
change_h160 = p.point.hash160()
change_script = p2pkh_script(change_h160)
change_output = TxOut(amount=change_amount, script_pubkey=change_script)

#OP_RETURN output
'''create da shit'''


#create transaction, sign and send
tx_obj = Tx(1, [tx_in], [change_output, target_output, secret_output], locktime = 0, testnet = True)
tx_obj.sign_input(0, p)
node.send(tx_obj)

print('TransactionID:', tx_obj.id())

