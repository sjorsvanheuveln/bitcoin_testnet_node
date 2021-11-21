#!/usr/bin/env python3

'''
Bitcoin Blockchain Parser
Parse the blockchain and save the data to a database and perform analysis.
SvH 18-11-2021
'''

####################################
from database import *


'''fill db'''
blocks = get_block(10000)
db = Database('blocks')
db.drop()
db.add_multiple(blocks)
db.height_update()

#plot(db.sort(), 'difficulty')

