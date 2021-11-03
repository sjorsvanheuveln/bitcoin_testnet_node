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
from helpers import SIGHASH_ALL
from tx import *

raw_tx = ('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
stream = BytesIO(bytes.fromhex(raw_tx))
transaction = Tx.parse(stream)

z = transaction.sig_hash(0)
private_key = PrivateKey(secret=8675309)
der = private_key.sign(z).der()
sig = der + SIGHASH_ALL.to_bytes(1, 'big')
sec = private_key.point.sec()
script_sig = Script([sig, sec])
transaction.tx_ins[0].script_sig = script_sig 
print(transaction.serialize().hex())

####################################