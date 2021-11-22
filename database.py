#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient, ReturnDocument
import random
from network import *
from tx import Tx
from pprint import pformat
import matplotlib.pyplot as plt
import glob


GENESIS_HASH = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
PATH = '/Users/sjorsvanheuveln/Library/Application Support/Bitcoin/blocks/'

class Database:

    def __init__(self, collection_name, drop=False):
        self.collection = MongoClient('mongodb://127.0.0.1:27017')['bittest'][collection_name]
        if drop: self.drop() #removes collection including indexes
        self.collection.create_index([('prev_block', 1)]) #12x performance improvement

    def __repr__(self):
        '''using pretty print library here'''
        return pformat(list(self.collection.find()))
    
    def add(self, block, i=''):
        '''adds a block to the database'''
        if not self.is_in_collection(block.id()):
            print('Adding: {}:'.format(str(i).zfill(6)), block.id(), end='\r')
            self.collection.insert_one(block.mongodb_object())

    def add_multiple(self, blocks):
        for i, block in enumerate(blocks):
            self.add(block, i)

    def is_in_collection(self, blockhash):
        '''checks if block is already in db'''
        result = self.collection.find_one({"_id": blockhash})
        return False if result == None else True

    def drop(self):
        '''removes the collection'''
        self.collection.drop()

    def latest_block(self):
        '''returns block with maximum registered height'''
        return self.collection.find_one(sort=[("height", -1)])

    # def next_block(self, block_id):
    #     '''returns the next block given prev_hash'''
    #     print('next block', block_id)
    #     return self.collection.find({'prev_block': block_id})

    def update_block_heights(self):
        '''Adds height to new blocks'''
        #perhaps can still improve by retrieve all at once update all and then update database
        start_block = self.latest_block()
        print('\n')

        while True:
            next_block_query = { 'prev_block': start_block['_id'] }
            new_height = {"$set": {'height': start_block['height'] + 1}}
            start_block = self.collection.find_one_and_update(next_block_query, new_height, return_document=ReturnDocument.AFTER)
            
            if start_block == None: break
            print('New height:', start_block['height'], end='\r')

    def plot(self, attribute, interval, scale = 'linear'):
        records = list(self.collection.find({'height':  interval}).sort('height'))
        attr_list = [r[attribute] for r in records]
        plt.plot(attr_list)
        plt.title(attribute.title())
        plt.xlabel('block height')
        plt.yscale(scale)
        plt.show()



class Block:

    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce, tx_count = None, tx = None):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.tx_count = tx_count
        self.tx = tx

    def __repr__(self):
        return 'Blockhash: {} tx:{}'.format(self.id(), self.tx_count)

    @classmethod
    def parse(cls, s, parse_tx_flag):
        magic = s.read(4)
        if magic != NETWORK_MAGIC:
            raise ValueError('magic not correct')

        size = little_endian_to_int(s.read(4))

        version = little_endian_to_int(s.read(4))
        prev_block = s.read(32)[::-1]
        merkle_root = s.read(32)[::-1]
        timestamp = little_endian_to_int(s.read(4))
        bits = s.read(4)
        nonce = s.read(4)

        #transactions
        tx = []
        if parse_tx_flag:
            tx_count = read_varint(s)
            for i in range(tx_count): tx.append(Tx.parse(s))
        else:
            tx_count = None
            s.read(size - 80)

        return cls(version, prev_block, merkle_root, timestamp, bits, nonce, tx_count, tx)

    def serialize(self):
        '''Returns the 80 byte block header'''
        result = int_to_little_endian(self.version, 4)
        result += self.prev_block[::-1]
        result += self.merkle_root[::-1]
        result += int_to_little_endian(self.timestamp, 4)
        result += self.bits
        result += self.nonce
        return result

    def mongodb_object(self):
        '''serialize for mongoDB object'''
        return {
            "_id": self.id(),
            "height": 0 if self.id() == GENESIS_HASH else None,
            "prev_block": self.prev_block.hex().zfill(64),
            "merkle_root": self.merkle_root.hex().zfill(64),
            "tx_count": self.tx_count,
            "difficulty": self.difficulty(),
            "timestamp": self.timestamp
            "tx": self.tx
            }

    def id(self):
        '''returns the blockhash'''
        return self.hash().hex().zfill(64)

    def hash(self):
        '''Returns the block hash'''
        s = self.serialize()
        h256 = hash256(s)
        return h256[::-1]

    def bip9(self):
        '''Returns whether this block is signaling readiness for BIP9'''
        return self.version >> 29 == 0b001

    def bip91(self):
        '''Returns whether this block is signaling readiness for BIP91'''
        return self.version >> 4 & 1 == 1

    def bip141(self):
        '''Returns whether this block is signaling readiness for BIP141'''
        return self.version >> 1 & 1 == 1

    def target(self):
        '''Returns the proof-of-work target based on the bits'''
        return bits_to_target(self.bits)

    def difficulty(self):
        '''Returns the block difficulty based on the bits'''
        lowest = 0xffff * 256**(0x1d - 3)
        return lowest / self.target()

    def check_pow(self):
        '''Returns whether this block satisfies proof of work'''
        h256 = hash256(self.serialize())
        proof = little_endian_to_int(h256)

        if not proof < self.target():
            raise ValueError('Invalid proof of work on:', b.hash())

        return True

class Record:

    def __init__(self):
        print('yo')
    #Or integrate into block. This should be possible.



def get_block(n, parse_tx_flag = True):
    
    blocks = []
    files = sorted(glob.glob(PATH + 'blk*.dat'))

    for file in files:

        print('Parsing', file, '\n', end='\r')
        s = open(file, 'rb')

        while s.peek(1) != b'':
            b = Block.parse(s, parse_tx_flag)
            blocks.append(b)
            if len(blocks) == n: return blocks

    return blocks
    

def create_interval(low, high):
    return {'$gte': low, '$lte': high}
