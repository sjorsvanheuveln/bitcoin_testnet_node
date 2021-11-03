#!/usr/bin/env python3

'''
Little Bitcoin Testnet Node project to write my first transaction (+more).
Author: Sjors van Heuveln 03-11-2021
'''

####################################
from examples import *
#basic_node_action()
####################################



####################################
# Transactions                     #
####################################

from ecc import PrivateKey
from network import SimpleNode
from helpers import decode_base58, SIGHASH_ALL, little_endian_to_int
from script import p2pkh_script, Script
from tx import TxIn, TxOut, Tx
from config import PASSPHRASE

e = little_endian_to_int(hash256(PASSPHRASE))
p = PrivateKey(e)
a = p.point.address(compressed=True, testnet=True)
print('my pubkey:', a)

prev_tx = bytes.fromhex('2a23ae7f643f3264e3ca284e17c754900461f2bb19cb16a017a24bedb699d59d')
prev_index = 1
tx_in = TxIn(prev_tx, prev_index)

#change output
change_amount = int(99000)
change_h160 = p.point.hash160()
change_script = p2pkh_script(change_h160)
change_output = TxOut(amount=change_amount, script_pubkey=change_script)

#target output
target_amount = int(900)
target_h160 = decode_base58('mnrVtF8DWjMu839VW3rBfgYaAfKk8983Xf')
target_script = p2pkh_script(target_h160)
target_output = TxOut(amount=target_amount, script_pubkey=target_script)
tx_obj = Tx(1, [tx_in], [change_output, target_output], locktime = 0, testnet = True)


# sign the one input in the transaction object using the private key
tx_obj.sign_input(0, p)
# print the transaction's serialization in hex
print('\n', tx_obj.serialize().hex(), '\n')
# broadcast at http://testnet.blockchain.info/pushtx

node = SimpleNode(TESTNET_HOST, testnet=True, logging=True)
node.handshake()
node.send(tx_obj)
feefilter = node.wait_for(FeefilterMessage)
print('min fee:', feefilter.fee)


####################################

''' todo

    1. What is happening with above transaction??? raw is different to final serialization
    2. How to make one myself on testnet -> book
    3. Send it with the node.
    4. Write a function that can find a utxo for my pubkey
    5. Spend that UTXO.
'''
