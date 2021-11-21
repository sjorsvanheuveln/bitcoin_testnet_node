#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient
import random
from network import *
from tx import Tx
from pprint import pformat
import matplotlib.pyplot as plt

GENESIS_HASH = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'


class Database:

    def __init__(self, collection_name):
        self.collection = MongoClient('mongodb://127.0.0.1:27017')['bittest'][collection_name]

    def __repr__(self):
        '''using pretty print library here'''
        return pformat(list(self.collection.find()))
    
    def add(self, block):
        '''adds a block to the database'''
        # build a check whether current hash is in db already
        self.collection.insert_one(block.mongodb_object())

    def is_in_collection(self, blockhash):
        result = self.collection.find({"_id": blockhash})
        print('result', list(result))

    def add_multiple(self, blocks):
        for block in blocks:
            self.add(block)

    def drop(self):
        '''removes the collection'''
        self.collection.drop()

    def insert_fake(self):
        new_id = random.randint(0, 1000000)
        self.collection.insert_one({"name": "sjors", "score": 5})

    def blockheight_sort(self):
        raise NotImplementedError()

      

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
    def parse(cls, s):
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

        tx_count = read_varint(s)
        tx = []
        for i in range(tx_count): tx.append(Tx.parse(s))

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
            "merkle_root": self.prev_block.hex().zfill(64),
            "tx_count": self.tx_count,
            "difficulty": self.difficulty()
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

def get_block(n, files = 1):
    path = '/Users/sjorsvanheuveln/Library/Application Support/Bitcoin/blocks/'
    blocks = []

    for i in range(0, files):
        print('blk', i)
        s = open(path + "blk" + str(i).zfill(5) + ".dat", "rb")
        while s.peek(1) != b'':
            b = Block.parse(s)
            blocks.append(b)
            print(len(blocks) - 1, b)
            if len(blocks) == n: break

    return blocks


def plot(blocks):
    counts = [b.difficulty() for b in blocks]
    plt.plot(counts)
    plt.show()
      

