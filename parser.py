#!/usr/bin/env python3

'''
Bitcoin Blockchain Parser
Parse the blockchain and save the data to a database and perform analysis.
SvH 18-11-2021
'''

####################################
from database import *


'''fill db'''
blocks = get_block(100)
db = Database('blocks')
#db.drop()
db.add_multiple(blocks)

#db = Database('blocks')

#res = db.collection.find({'prev_block': db.latest_block()['_id']})
#print(list(res))
db.height_update()
res = db.latest_block()
print(res)



#plot(blocks)






