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
from script import *

#basic_node_action(TESTNET_HOST2)
#send_transaction()
#getMempool(TESTNET_HOST2)
#bloomfilter()
#send_ascii_tx(bytes('wzup bitcoiners', 'ascii'), testnet=True)
#art_from_chain('d8ca2c1cc697c4125d2bd5bcbaa5c3a6a54e32752d29ccb0244ed7ce24bdcbaf', testnet=False)
#art_from_chain('a9ef5d93aa87b8bc065055b9b5e9e116b92f77974c95ac51bbf9d9e4a9f5b77c', testnet=True) #saylor

#send_simple_tx(RETURN_COIN_FAUCET_ADDRESS)
####################################

testnet = True
e = little_endian_to_int(hash256(PASSPHRASE))
p = PrivateKey(e)
a = p.point.address(testnet = testnet)
print(a)
msg = bytes("Sup testnet!", 'ascii')


#txin
tx_in = TxFetcher.max_utxo_fetch(address = a, testnet=testnet)


outputs = []
'''hand shake and get min fee'''
node = SimpleNode(TESTNET_HOST2, testnet=testnet, logging=True)
node.handshake()
min_fee = node.wait_for(FeefilterMessage).fee

#opreturn output
payload_amount = 0
payload_script = secret_script(msg)
outputs.append(TxOut(amount=payload_amount, script_pubkey=payload_script))


#change output
change_amount = int(tx_in.amount - min_fee)
change_h160 = p.point.hash160()
change_script = p2pkh_script(change_h160)
outputs.append(TxOut(amount=change_amount, script_pubkey=change_script))


#create transaction, sign and send
tx_obj = Tx(1, [tx_in], outputs, locktime = 0, testnet = testnet)
tx_obj.sign_input(0, p)
node.send(tx_obj)

print('wait for reject msg')
reject = node.wait_for(RejectMessage)
print(reject)


