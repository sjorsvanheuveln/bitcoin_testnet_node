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
#send_ascii_tx(bytes('wzup bitcoiners', 'ascii'))
art_from_chain('10ac071ab97dfff11121f4caae401437c9a180b90f0de81915f4b44d088e71fd', testnet=False)
#send_simple_tx(RETURN_COIN_FAUCET_ADDRESS)
####################################


'''waiting for:
c79037d71c3fab841e80f371e1ef21ed70e7d857f9adad920f563c771f55e9da
502ad1b0b7823a6babb30e9ffba53351e895e6a4ffce351dbd11a1e782c741b0
aa1605bd35c6f60a4fc17f54cd9720f728dd0d0f5ad2543e7cf0ae2ea69e37c7
'''

# e = little_endian_to_int(hash256(PASSPHRASE))
# p = PrivateKey(e)
# a = p.point.address(testnet = False)
# print(a)
# msg = bytes("Hello Mainnet!", 'ascii')


# #txin
# tx_in = TxFetcher.max_utxo_fetch(address = a, testnet=False)


# outputs = []
# '''hand shake and get min fee'''
# node = SimpleNode(TESTNET_HOST3, testnet=False, logging=True)
# node.handshake()

# min_fee = node.wait_for(FeefilterMessage).fee
# if min_fee < 100:
#     min_fee = 250
#     print('reset fee to:', min_fee)

# #opreturn output
# payload_amount = 0
# payload_script = secret_script(msg)
# outputs.append(TxOut(amount=payload_amount, script_pubkey=payload_script))


# #change output
# change_amount = int(tx_in.amount - min_fee)
# change_h160 = p.point.hash160()
# change_script = p2pkh_script(change_h160)
# outputs.append(TxOut(amount=change_amount, script_pubkey=change_script))


# #create transaction, sign and send
# tx_obj = Tx(1, [tx_in], outputs, locktime = 0, testnet = False)
# tx_obj.sign_input(0, p)
# node.send(tx_obj)

# print('wait for reject msg')
# reject = node.wait_for(RejectMessage)
# print(reject)


