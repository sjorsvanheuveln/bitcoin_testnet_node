#!/usr/bin/env python3

'''
Bitcoin Blockchain Parser
Parse the blockchain and save the data to a database and perform analysis.
SvH 18-11-2021
'''

####################################
from database import *


'''fill db'''
blocks = get_block(100000, parse_tx_flag = False)
db = Database('blocks')
#db.drop()
db.add_multiple(blocks)
db.update_block_heights()
#plot(db.sort(), 'difficulty')












''' TODO
1. Try to retrieve transactions from DB
    - Store Transactions separately into new collections.
2. Make a function that will correctly update the database to the latest block on my node.
3. Timestamp to date?
4. Improve update_height function.
    - Perhaps search within a range. 
    - Or exclude records with height
    - Or calculate height before initial store to db!
'''



