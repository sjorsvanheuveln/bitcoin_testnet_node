#!/usr/bin/env python3

'''
Bitcoin Blockchain Parser
Parse the blockchain and save the data to a database and perform analysis.
SvH 18-11-2021
'''

####################################
from database import *
import time
from parse_examples import *
from datetime import datetime

''' examples '''
#plot_difficulty()

'''fill db'''
blocks = get_block(10, parse_tx_flag = True)
db = Database('blocks', drop=False)
db.add_multiple(blocks)
db.update_block_heights()

r = db.collection.find_one({'height': 5})
print(r)






''' TODO
1. Try to retrieve transactions from DB
    - Store Transactions separately into new collections.
2. Make a function that will correctly update the database to the latest block on my node.

'''


# start = time.time()
# end = time.time()
# print('Time:', end - start)

#3. Timestamp to date?
# res = db.collection.find_one({'height': 150000}, {'timestamp': 1})
# print(datetime.utcfromtimestamp(res['timestamp']).strftime('%Y-%m-%d %H:%M:%S'))