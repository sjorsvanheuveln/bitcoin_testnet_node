from io import BytesIO

from helpers import (
    bits_to_target,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint
)

#block serialization
GENESIS_BLOCK = BytesIO(bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c'))
TESTNET_GENESIS_BLOCK = BytesIO(bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff001d1aa4ae18'))
LOWEST_BITS = bytes.fromhex('ffff001d')

#hashes
genesis_block= bytes.fromhex('000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f')
block_3 = bytes.fromhex('0000000082b5015589a3fdf2d4baff403e6f0be035a5d9742c1cae6295464449')
testnet_genesis_block = bytes.fromhex('000000000933ea01ad0ee984209779baaec3ced90fa3f408719526f8d77f4943')
testnet_block_3 = bytes.fromhex('000000008b896e272758da5297bcd98fdc6d97c9b765ecec401e286dc1fdbe10')

class Block:

    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce, tx_hashes = None, tx_count = None, tx = None):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.tx_hashes = tx_hashes
        self.tx_count = tx_count
        self.tx = tx

    def __repr__(self):
        return '\nBlockhash: {}'.format(self.hash().hex().zfill(64))

    @classmethod
    def parse(cls, s, full_block = False):
        '''Takes a byte stream and parses a block. Returns a Block object'''
        version = little_endian_to_int(s.read(4))
        prev_block = s.read(32)[::-1]
        merkle_root = s.read(32)[::-1]
        timestamp = little_endian_to_int(s.read(4))
        bits = s.read(4)
        nonce = s.read(4)

        if not full_block:
            return cls(version, prev_block, merkle_root, timestamp, bits, nonce)

        tx_count = read_varint(s)
        tx = s.read(tx_count)
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

