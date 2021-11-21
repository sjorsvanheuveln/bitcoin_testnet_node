#!/usr/bin/env python3

'''
Bitcoin Blockchain Parser
Parse the blockchain and save the data to a database and perform analysis.
SvH 18-11-2021
'''

####################################
from database import *


blocks = get_block(100)
db = Database('blocks')
db.drop()
db.add_multiple(blocks)
#db.drop()
db.is_in_collection(blocks[0].id())




#plot(blocks)






