''' Transaction Classes '''
from io import BytesIO

import json
import requests

from ecc import PrivateKey
from helpers import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    SIGHASH_ALL,
)
from script import p2pkh_script, Script


class TxFetcher:
    cache = {}
    
    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            return 'https://blockstream.info/testnet/api'
        else:
            return 'https://blockstream.info/api'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False):
        if fresh or (tx_id not in cls.cache):
            url = '{}/tx/{}/hex'.format(cls.get_url(testnet), tx_id)
            response = requests.get(url)
            try:
                raw = bytes.fromhex(response.text.strip())
            except ValueError:
                raise ValueError('unexpected response: {}'.format(response.text))
            tx = Tx.parse(BytesIO(raw), testnet=testnet)
            # make sure the tx we got matches to the hash we requested
            if tx.segwit:
                computed = tx.id()
            else:
                computed = hash256(raw)[::-1].hex()
            if computed != tx_id:
                raise RuntimeError('server lied: {} vs {}'.format(computed, tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]

    @classmethod
    def max_utxo_fetch(cls, address, testnet=True):
        '''find the tx and id with most amount to spend from address'''
        url = '{}/address/{}/utxo'.format(cls.get_url(testnet), address)
        response = requests.get(url)
        
        try:
            raw = json.loads(response.text)
        except ValueError:
            raise ValueError('unexpected response: {}'.format(response.text))

        amounts = [tx['value'] for tx in raw]
        max_index = amounts.index(max(amounts))

        prev_tx = bytes.fromhex(raw[max_index]['txid'])
        prev_index = raw[max_index]['vout']

        tx_in = TxIn(prev_tx, prev_index)
        tx_in.amount = amounts[max_index]
        cls.cache[address] = tx_in

        return cls.cache[address]

    @classmethod
    def load_cache(cls, filename):
        disk_cache = json.loads(open(filename, 'r').read())
        for k, raw_hex in disk_cache.items():
            cls.cache[k] = Tx.parse(BytesIO(bytes.fromhex(raw_hex)))

    @classmethod
    def dump_cache(cls, filename):
        with open(filename, 'w') as f:
            to_dump = {k: tx.serialize().hex() for k, tx in cls.cache.items()}
            s = json.dumps(to_dump, sort_keys=True, indent=4)
            f.write(s)


class Tx:
    '''This class is also a message to be received by the node'''
    command = b'tx'

    def __init__(self, version, tx_ins, tx_outs, 
        locktime, testnet=False, segwit=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet
        self.segwit = segwit
        self._hash_prevouts = None
        self._hash_sequence = None
        self._hash_outputs = None

    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime,
        )

    def id(self):
        '''Human-readable hexadecimal of the transaction hash'''
        return self.hash().hex()

    def hash(self):
        '''Binary hash of the legacy serialization'''
        return hash256(self.serialize_legacy())[::-1]

    @classmethod
    def parse(cls, s, testnet=False):
        s.read(4)
        if s.read(1) == b'\x00':
            parse_method = cls.parse_segwit
        else:
            parse_method = cls.parse_legacy
        s.seek(-5, 1)
        return parse_method(s, testnet=testnet)

    @classmethod
    def parse_legacy(cls, s, testnet=False):
        version = little_endian_to_int(s.read(4))
        num_inputs = read_varint(s)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        num_outputs = read_varint(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        locktime = little_endian_to_int(s.read(4))
        return cls(version, inputs, outputs, locktime, 
                   testnet=testnet, segwit=False)

    @classmethod
    def parse_segwit(cls, s, testnet=False):
        version = little_endian_to_int(s.read(4))
        marker = s.read(2)
        if marker != b'\x00\x01':  # <1>
            raise RuntimeError('Not a segwit transaction {}'.format(marker))
        num_inputs = read_varint(s)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        num_outputs = read_varint(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        for tx_in in inputs:  # <2>
            num_items = read_varint(s)
            items = []
            for _ in range(num_items):
                item_len = read_varint(s)
                if item_len == 0:
                    items.append(0)
                else:
                    items.append(s.read(item_len))
            tx_in.witness = items
        locktime = little_endian_to_int(s.read(4))
        return cls(version, inputs, outputs, locktime, 
                   testnet=testnet, segwit=True)

    def serialize(self):
        if self.segwit:
            return self.serialize_segwit()
        else:
            return self.serialize_legacy()

    def serialize_legacy(self):  # <1>
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result

    def serialize_segwit(self):
        result = int_to_little_endian(self.version, 4)
        result += b'\x00\x01'
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        for tx_in in self.tx_ins:
            result += int_to_little_endian(len(tx_in.witness), 1)
            for item in tx_in.witness:
                if type(item) == int:
                    result += int_to_little_endian(item, 1)
                else:
                    result += encode_varint(len(item)) + item
        result += int_to_little_endian(self.locktime, 4)
        return result

    def size(self):
        '''calculates transaction size and fee_rate'''
        raw = len(self.serialize())
        segwit = 0
        if self.segwit == True:
            for txin in self.tx_ins:
                for item in txin.witness:
                    #count whether there are ops???
                    segwit += len(item)
            segwit += 5 #market, flag, len and 2 varints

        non_segwit = raw - segwit
        wu = 4 * non_segwit + segwit
        vsize = round(wu / 4, 2)
        fee = self.fee()
        sats_per_byte = round(fee / raw, 2)
        sats_per_vbyte = round(fee / vsize, 2)

        return '\nraw size: {}\nWU: {}\nvSize: {}\nSats/B: {}\nSats/vB: {}\n'.format(raw, wu, vsize, sats_per_byte, sats_per_vbyte)


    def fee(self):
        '''Returns the fee of this transaction in satoshi'''
        # initialize input sum and output sum
        input_sum, output_sum = 0, 0
        # use TxIn.value() to sum up the input amounts
        for tx_in in self.tx_ins:
            input_sum += tx_in.value(self.testnet)
        # use TxOut.amount to sum up the output amounts
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        # fee is input sum - output sum
        return input_sum - output_sum

    def sig_hash(self, input_index, redeem_script=None):
        '''Returns the integer representation of the hash that needs to get
        signed for index input_index'''
        # start the serialization with version
        # use int_to_little_endian in 4 bytes
        s = int_to_little_endian(self.version, 4)
        # add how many inputs there are using encode_varint
        s += encode_varint(len(self.tx_ins))
        # loop through each input using enumerate, so we have the input index
        for i, tx_in in enumerate(self.tx_ins):
            # if the input index is the one we're signing
            if i == input_index:
                # if the RedeemScript was passed in, that's the ScriptSig
                if redeem_script:
                    script_sig = redeem_script
                # otherwise the previous tx's ScriptPubkey is the ScriptSig
                else:
                    script_sig = tx_in.script_pubkey(self.testnet)
            # Otherwise, the ScriptSig is empty
            else:
                script_sig = None
            # add the serialization of the input with the ScriptSig we want
            s += TxIn(
                prev_tx=tx_in.prev_tx,
                prev_index=tx_in.prev_index,
                script_sig=script_sig,
                sequence=tx_in.sequence,
            ).serialize()
        # add how many outputs there are using encode_varint
        s += encode_varint(len(self.tx_outs))
        # add the serialization of each output
        for tx_out in self.tx_outs:
            s += tx_out.serialize()
        # add the locktime using int_to_little_endian in 4 bytes
        s += int_to_little_endian(self.locktime, 4)
        # add SIGHASH_ALL using int_to_little_endian in 4 bytes
        s += int_to_little_endian(SIGHASH_ALL, 4)
        # hash256 the serialization
        h256 = hash256(s)
        # convert the result to an integer using int.from_bytes(x, 'big')
        return int.from_bytes(h256, 'big')

    def hash_prevouts(self):
        if self._hash_prevouts is None:
            all_prevouts = b''
            all_sequence = b''
            for tx_in in self.tx_ins:
                all_prevouts += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
                all_sequence += int_to_little_endian(tx_in.sequence, 4)
            self._hash_prevouts = hash256(all_prevouts)
            self._hash_sequence = hash256(all_sequence)
        return self._hash_prevouts

    def hash_sequence(self):
        if self._hash_sequence is None:
            self.hash_prevouts()  # this should calculate self._hash_prevouts
        return self._hash_sequence

    def hash_outputs(self):
        if self._hash_outputs is None:
            all_outputs = b''
            for tx_out in self.tx_outs:
                all_outputs += tx_out.serialize()
            self._hash_outputs = hash256(all_outputs)
        return self._hash_outputs

    def sig_hash_bip143(self, input_index, redeem_script=None, witness_script=None):
        '''Returns the integer representation of the hash that needs to get
        signed for index input_index'''
        tx_in = self.tx_ins[input_index]
        # per BIP143 spec
        s = int_to_little_endian(self.version, 4)
        s += self.hash_prevouts() + self.hash_sequence()
        s += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
        if witness_script:
            script_code = witness_script.serialize()
        elif redeem_script:
            script_code = p2pkh_script(redeem_script.cmds[1]).serialize()
        else:
            script_code = p2pkh_script(tx_in.script_pubkey(self.testnet).cmds[1]).serialize()
        s += script_code
        s += int_to_little_endian(tx_in.value(), 8)
        s += int_to_little_endian(tx_in.sequence, 4)
        s += self.hash_outputs()
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)
        return int.from_bytes(hash256(s), 'big')

    def verify_input(self, input_index):
        '''Returns whether the input has a valid signature'''
        # get the relevant input
        tx_in = self.tx_ins[input_index]
        # grab the previous ScriptPubKey
        script_pubkey = tx_in.script_pubkey(testnet=self.testnet)
        # check to see if the ScriptPubkey is a p2sh
        if script_pubkey.is_p2sh_script_pubkey():
            # the last cmd has to be the RedeemScript to trigger
            #this should be added onto the tx_in script commands
            #redeem scripts should be stored off-chain!!!
            cmd = tx_in.script_sig.cmds[-1]
            # parse the RedeemScript
            raw_redeem = int_to_little_endian(len(cmd), 1) + cmd
            redeem_script = Script.parse(BytesIO(raw_redeem))
            # the RedeemScript might be p2wpkh or p2wsh
            if redeem_script.is_p2wpkh_script_pubkey():
                z = self.sig_hash_bip143(input_index, redeem_script)
                witness = tx_in.witness
            elif redeem_script.is_p2wsh_script_pubkey():
                cmd = tx_in.witness[-1]
                raw_witness = encode_varint(len(cmd)) + cmd
                witness_script = Script.parse(BytesIO(raw_witness))
                z = self.sig_hash_bip143(input_index, witness_script=witness_script)
                witness = tx_in.witness
            else:
                #if p2sh
                z = self.sig_hash(input_index, redeem_script)
                witness = None
        else:
            # ScriptPubkey might be a p2wpkh, p2wsh or p2pkh
            if script_pubkey.is_p2wpkh_script_pubkey():
                z = self.sig_hash_bip143(input_index)
                witness = tx_in.witness
            elif script_pubkey.is_p2wsh_script_pubkey():
                cmd = tx_in.witness[-1]
                raw_witness = encode_varint(len(cmd)) + cmd
                witness_script = Script.parse(BytesIO(raw_witness))
                z = self.sig_hash_bip143(input_index, witness_script=witness_script)
                witness = tx_in.witness
            else:
                #p2pkh
                z = self.sig_hash(input_index)
                witness = None
        # combine the current ScriptSig and the previous ScriptPubKey
        combined = tx_in.script_sig + script_pubkey
        # evaluate the combined script
        return combined.evaluate(z, witness)

    def verify(self):
        '''Verify this transaction'''
        # check that we're not creating money
        if self.fee() < 0:
            return False
        # check that each input has a valid ScriptSig
        for i in range(len(self.tx_ins)):
            if not self.verify_input(i):
                return False
        return True

    def sign_input(self, input_index, private_key, segwit = False):
        '''Signs the input using the private key'''
        # get the signature hash (z)
        z = self.sig_hash_bip143(input_index) if segwit else self.sig_hash(input_index)
     
        # get der signature of z from private key
        der = private_key.sign(z).der()
        # append the SIGHASH_ALL to der (use SIGHASH_ALL.to_bytes(1, 'big'))
        sig = der + SIGHASH_ALL.to_bytes(1, 'big')
        # calculate the sec
        sec = private_key.point.sec()
        # initialize a new script with [sig, sec] as the cmds
        script_sig = Script([sig, sec])

        # change input's script_sig to new script
        if segwit:
            self.tx_ins[input_index].witness = [sig, sec]
        else:
            self.tx_ins[input_index].script_sig = script_sig

        # return whether sig is valid using self.verify_input
        return self.verify_input(input_index)

    def is_coinbase(self):
        '''Returns whether this transaction is a coinbase transaction or not'''
        # check that there is exactly 1 input
        if len(self.tx_ins) != 1:
            return False
        # grab the first input
        first_input = self.tx_ins[0]
        # check that first input prev_tx is b'\x00' * 32 bytes
        if first_input.prev_tx != b'\x00' * 32:
            return False
        # check that first input prev_index is 0xffffffff
        if first_input.prev_index != 0xffffffff:
            return False
        return True

    def coinbase_height(self):
        '''Returns the height of the block this coinbase transaction is in
        Returns None if this transaction is not a coinbase transaction
        '''
        # if this is NOT a coinbase transaction, return None
        if not self.is_coinbase():
            return None
        # grab the first cmd
        first_cmd = self.tx_ins[0].script_sig.cmds[0]
        # convert the cmd from little endian to int
        return little_endian_to_int(first_cmd)


class TxIn:

    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence
        self.amount = None #added this for utxo fetch

    def __repr__(self):
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        )

    @classmethod
    def parse(cls, s):
        '''Takes a byte stream and parses the tx_input at the start
        return a TxIn object
        '''
        # prev_tx is 32 bytes, little endian
        prev_tx = s.read(32)[::-1]
        # prev_index is an integer in 4 bytes, little endian
        prev_index = little_endian_to_int(s.read(4))
        # use Script.parse to get the ScriptSig
        script_sig = Script.parse(s)
        # sequence is an integer in 4 bytes, little-endian
        sequence = little_endian_to_int(s.read(4))
        # return an instance of the class (see __init__ for args)
        
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):
        '''Returns the byte serialization of the transaction input'''
        # serialize prev_tx, little endian
        result = self.prev_tx[::-1]
        # serialize prev_index, 4 bytes, little endian
        result += int_to_little_endian(self.prev_index, 4)
        # serialize the script_sig
        result += self.script_sig.serialize()
        # serialize sequence, 4 bytes, little endian
        result += int_to_little_endian(self.sequence, 4)
        return result

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        '''Get the outpoint value by looking up the tx hash
        Returns the amount in satoshi
        '''
        # use self.fetch_tx to get the transaction
        tx = self.fetch_tx(testnet=testnet)
        # get the output at self.prev_index
        # return the amount property
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):
        '''Get the ScriptPubKey by looking up the tx hash
        Returns a Script object
        '''
        # use self.fetch_tx to get the transaction
        tx = self.fetch_tx(testnet=testnet)
        # get the output at self.prev_index
        # return the script_pubkey property
        return tx.tx_outs[self.prev_index].script_pubkey


class TxOut:

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        '''Takes a byte stream and parses the tx_output at the start
        return a TxOut object
        '''
        # amount is an integer in 8 bytes, little endian
        amount = little_endian_to_int(s.read(8))
        # use Script.parse to get the ScriptPubKey
        script_pubkey = Script.parse(s)
        # return an instance of the class (see __init__ for args)
        return cls(amount, script_pubkey)

    def serialize(self):
        '''Returns the byte serialization of the transaction output'''
        # serialize amount, 8 bytes, little endian
        result = int_to_little_endian(self.amount, 8)
        # serialize the script_pubkey
        result += self.script_pubkey.serialize()
        return result



