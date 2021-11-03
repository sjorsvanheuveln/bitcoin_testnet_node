import socket
import time

from io import BytesIO
from helpers import *
from random import randint
from block import Block

NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'
TESTNET_NETWORK_MAGIC = b'\x0b\x11\x09\x07'

class NetworkEnvelope:
    def __init__(self, command, payload, testnet=False):
        self.command = command
        self.payload = payload
        if testnet:
            self.magic = TESTNET_NETWORK_MAGIC
        else:
            self.magic = NETWORK_MAGIC

    def __repr__(self):
        return '{}: {}'.format(self.command.decode('ascii'), self.payload.hex())

    @classmethod
    def parse(cls, s, testnet=False):
        magic = s.read(4)
        if magic == b'':
            raise RuntimeError('Connection reset!')
        if testnet:
            expected_magic = TESTNET_NETWORK_MAGIC
        else:
            expected_magic = NETWORK_MAGIC
        if magic != expected_magic:
            raise RuntimeError('magic is not right {} vs {}'.format(magic.hex(), expected_magic.hex()))

        cmd = s.read(12)
        cmd = cmd.decode('utf-8').rstrip('\x00').encode()
        p_length = little_endian_to_int(s.read(4))
        checksum = s.read(4)
        payload = s.read(p_length)
        
        # verify checksum
        if not hash256(payload)[0:4] == checksum:
            raise RuntimeError('Bad Checksum!')
        
        return cls(cmd, payload)

    def serialize(self):
        '''Returns the byte serialization of the entire network message'''
        # add the network magic
        result = self.magic
        result += self.command + (12 - len(self.command)) * b'\x00'
        result += int_to_little_endian(len(self.payload), 4)        
        result += hash256(self.payload)[0:4]
        result += self.payload
        
        return result

    def stream(self):
        return BytesIO(self.payload)


class VersionMessage:
    command = b'version'

    def __init__(self, version=70015, services=0, timestamp=None,
                 receiver_services=0,
                 receiver_ip=b'\x00\x00\x00\x00', receiver_port=8333,
                 sender_services=0,
                 sender_ip=b'\x00\x00\x00\x00', sender_port=8333,
                 nonce=None, user_agent=b'/programmingbitcoin:0.1/',
                 latest_block=0, relay=False):
        self.version = version
        self.services = services
        if timestamp is None:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.receiver_services = receiver_services
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.sender_services = sender_services
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        if nonce is None:
            self.nonce = int_to_little_endian(randint(0, 2**64), 8)
        else:
            self.nonce = nonce
        self.user_agent = user_agent
        self.latest_block = latest_block
        self.relay = relay

    @classmethod
    def parse(cls, s):
        version = little_endian_to_int(s.read(4))
        services = little_endian_to_int(s.read(8))
        timestamp = little_endian_to_int(s.read(8))
        receiver_services = little_endian_to_int(s.read(8))
        receiver_ip = s.read(16)
        receiver_port = s.read(2)
        sender_services = little_endian_to_int(s.read(8))
        sender_ip = s.read(16)
        sender_port = s.read(2)
        nonce = s.read(8)
        user_agent_length = read_varint(s)
        user_agent = s.read(user_agent_length)
        latest_block = little_endian_to_int(s.read(4))
        relay = True if s.read(1) == b'\x01' else False
        
        return cls(version, services, timestamp,
                 receiver_services,
                 receiver_ip, receiver_port,
                 sender_services,
                 sender_ip, sender_port,
                 nonce, user_agent,
                 latest_block, relay)

    def serialize(self):
        '''Serialize this message to send over the network'''
        ipv4 = 10 * b'\x00' + 2* b'\xff'
        
        result = int_to_little_endian(self.version, 4)
        result += int_to_little_endian(self.services, 8)
        result += int_to_little_endian(self.timestamp, 8)
        result += int_to_little_endian(self.receiver_services, 8)
        result += ipv4 + self.receiver_ip
        result += self.receiver_port.to_bytes(2, 'big')
        result += int_to_little_endian(self.sender_services, 8)
        result += ipv4 + self.sender_ip
        result += self.sender_port.to_bytes(2, 'big')
        result += self.nonce + (8 - len(self.nonce)) * b'\x00'
        result += encode_varint(len(self.user_agent))
        result += self.user_agent
        result += int_to_little_endian(self.latest_block, 4)
        
        if self.relay:
            result += b'x\01'
        else:
            result += b'\x00'
        return result

class VerAckMessage:
    command = b'verack'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return cls()

    def serialize(self):
        return b''

class PingMessage:
    command = b'ping'

    def __init__(self, nonce):
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce

class PongMessage:
    command = b'pong'

    def __init__(self, nonce):
        self.nonce = nonce

    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce

class GetAddressMessage:
    command = b'getaddr'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return cls()

    def serialize(self):
        return b''

class AddressMessage:
    command = b'addr'

    def __init__(self, count, addr_list):
        self.count = count
        self.addr_list = addr_list

    def __repr__(self):
        return 'Number of addresses: {}\n {}'.format(self.count, self.addr_list)

    @classmethod
    def parse(cls, s):
        count = read_varint(s)
        addr_list = []

        for addr in range(count):
          addr_list.append(NetAddress.parse(s))
          #

        return cls(count, addr_list)

    def serialize(self):
        raise NotImplementedError('Serialization not yet implemented!')

class GetHeadersMessage:
    '''Request Headers'''
    command = b'getheaders'

    def __init__(self, version=70015, num_hashes=1, 
        start_block=None, end_block=None):
        self.version = version
        self.num_hashes = num_hashes
        if start_block is None:
            raise RuntimeError('a start block is required')
        self.start_block = start_block
        if end_block is None:
            self.end_block = b'\x00' * 32
        else:
            self.end_block = end_block

    def serialize(self):
        '''Serialize this message to send over the network'''
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(self.num_hashes)
        result += self.start_block[::-1]
        result += self.end_block[::-1]
        return result

class HeadersMessage:
    '''Receive Headers'''
    command = b'headers'

    def __init__(self, blocks):
        self.blocks = blocks

    @classmethod
    def parse(cls, stream):
        num_headers = read_varint(stream)
        blocks = []
        for _ in range(num_headers):
            blocks.append(Block.parse(stream))
            num_txs = read_varint(stream)
            if num_txs != 0:
                raise RuntimeError('number of txs not 0')
        return cls(blocks)


class SimpleNode:

    def __init__(self, host, port=None, testnet=False, logging=False):
        if port is None:
            if testnet:
                port = 18333
            else:
                port = 8333
        self.testnet = testnet
        self.logging = logging
        # connect to socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        # create a stream that we can use with the rest of the library
        self.stream = self.socket.makefile('rb', None)

    def handshake(self):
        '''Do a handshake with the other node.
        Handshake is sending a version message and getting a verack back.'''
        version = VersionMessage()
        self.send(version)
        self.wait_for(VerAckMessage)

    def getAddressesFromHost(self):
        ''' Get peers from host'''
        getaddress = GetAddressMessage()
        self.send(getaddress)
        print('retrieving addresses')
        address = self.wait_for(AddressMessage)
        print(address.addr_list)

    def send(self, message):
        '''Send a message to the connected node'''
        envelope = NetworkEnvelope(message.command, message.serialize(), testnet=self.testnet)
        
        if self.logging:
            print('sending: {}'.format(envelope))

        self.socket.sendall(envelope.serialize())

    def read(self):
        '''Read a message from the socket'''
        envelope = NetworkEnvelope.parse(self.stream, testnet=self.testnet)
        if self.logging:
            print('receiving: {}'.format(envelope))
        return envelope

    def wait_for(self, *message_classes):
        '''Wait for one of the messages in the list'''
        # initialize the command we have, which should be None
        command = None
        command_to_class = {m.command: m for m in message_classes}
        # loop until the command is in the commands we want
        while command not in command_to_class.keys():
            # get the next network message
            envelope = self.read()
            # set the command to be evaluated
            command = envelope.command
            # we know how to respond to version and ping, handle that here
            if command == VersionMessage.command:
                # send verack
                self.send(VerAckMessage())
            elif command == PingMessage.command:
                # send pong
                self.send(PongMessage(envelope.payload))
            elif command == AddressMessage.command:
                print('Address received trigger')
            elif command == HeadersMessage.command:
                print('Headers received trigger')

        # return the envelope parsed as a member of the right message class
        return command_to_class[command].parse(envelope.stream())

class NetAddress:
    def __init__(self, time, services, ipv, port):
      self.time = time
      self.services = services
      self.ipv = ipv
      self.port = port

    def __repr__(self):
        return '\nTime: {}\nServices: {}\nipv: {}\nport: {}\n'.format(
          self.time, self.services, bytes_to_ip(self.ipv[-4:]), int.from_bytes(self.port, 'big')
        )

    @classmethod
    def parse(cls, s):
        time = little_endian_to_int(s.read(4))
        services = little_endian_to_int(s.read(8))
        ipv = s.read(16)
        port = s.read(2)
        
        return cls(time, services, ipv, port)

    def serialize(self):
        raise NotImplementedError('Serialization not yet implemented!')

