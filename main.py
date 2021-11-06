#!/usr/bin/env python3

'''
Little Bitcoin Testnet Node project to write my first transaction (+more).
Author: Sjors van Heuveln 03-11-2021
'''

####################################
from examples import *
from helpers import *
from network import *

#basic_node_action(TESTNET_HOST2)
#send_transaction()
#getMempool(TESTNET_HOST2)
#bloomfilter()
####################################


#this transaction is messed up
#try to implement something that can filter this shit.
# tx_hex_dump = '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff1d03e50b20045bee726100a0000031010000000a4d696e696e67636f726500000000020000000000000000266a24aa21a9edc003b4a02fa3d44cabbd38d51c7ac73ccf8b6222e1d9993e1d296982f550bf33384a4c00000000001976a914638b34ce24a0cdce5682032fb7edd0402b667dbb88ac00000000'
# tx_hex_dump2 = '02000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4803c90b200443b47261425443506f6f6cfabe6d6d8cd7b6ff17cf4544ac88396e6f987e4065c50f7699b7b08d519b200532da973b04000000243dccdc0200000eb5773f0000000000ffffffff02f55b4c000000000017a9147bef0b4a4dafa77b2ec52b81659cbcf0d9a91487870000000000000000266a24aa21a9ed3e7a3bbe89632a37506baa53f3aa642e58d9517cc432a08db96c05bd293cb80c00000000'
 
# Tx.parse(BytesIO(bytes.fromhex(tx_hex_dump)), testnet=True)




# def endian_swap(s):
#     swaps = ''
#     for i in range(0, len(s), 2):
#         swaps += s[i+1] + s[i]
#     print(swaps[::-1])



# s = '9b94830000000000'
# endian_swap(s)

# pubkey = bytes.fromhex('038707dbb5b851f7952e4451ee38859601d3937d0c9260cc3d376f145d425ebea9')
# print(pubkey)
# h160 = hash160(pubkey)
# print(h160.hex())
# extended_pubkey = b'\x6f' + h160

# # print(h160.hex())
# #print(extended_pubkey.hex())
# address = encode_base58_checksum(extended_pubkey)
# print(address)

# data = bytes.fromhex('2d2d2d424547494e20545249425554452d2d2d20')
# print(data.decode("ascii"))

len_sassaman_pretty()



