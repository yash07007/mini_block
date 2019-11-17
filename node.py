from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
import socket                
import pickle as pk
from bson.json_util import dumps
from bson.json_util import loads

class Node:
    def __init__(self, node_id, card_secret):
        self.private_key = None
        self.public_key = None
        self.data = None
        self.node_id = node_id
        self.download_data(card_secret)

    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()

    def save_keys(self):
        if(self.public_key != None and self.private_key != None):
            try:
                with open('data/node-{}-keys.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving keys failed...')
                return False


    def load_keys(self):
        try:
            with open('data/node-{}-keys.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                self.public_key, self.private_key = keys[0][:-1], keys[1]
            return True
        except (IOError, IndexError):
            print('Loading keys failed...')
            return False

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))

    def sign_transaction(self, nodeId, candidateId, partyId):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        payload = SHA256.new((str(nodeId) + str(candidateId) + str(partyId)).encode('utf8'))
        signature = signer.sign(payload)
        return binascii.hexlify(signature).decode('ascii')
    
    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.nodeId))
        verifier = PKCS1_v1_5.new(public_key)
        payload = SHA256.new((str(transaction.nodeId) + str(transaction.candidateId) + str(transaction.partyId)).encode('utf8'))
        return verifier.verify(payload, binascii.unhexlify(transaction.signature))

    def save_data(self):
        if(self.data != None):
            try:
                with open('data/node-{}-data.txt'.format(self.node_id), mode='w') as f:
                    f.write(dumps(self.data))
                return True
            except (IOError, IndexError):
                print('Saving constituency data failed...')
                return False

    def load_data(self):
        try:
            with open('data/node-{}-data.txt'.format(self.node_id), mode='r') as f:
                self.data = f.readlines()[0]
            return True
        except (IOError, IndexError):
            print('Loading constituency data failed...')
            return False

    def download_data(self, card_secret):
        s = socket.socket()                  
        s.connect(('localhost', 12345)) 
        s.send(pk.dumps(card_secret))
        data = pk.loads(s.recv(10000))
        s.close()
        self.data = dumps(data)
        if(self.save_data()):
            print('Downloaded data saved locally successfully')
        else:
            print('Please format and restart device...')    
        return None

    def get_data(self):
        if(self.data):
            return self.data
        else:
            self.data = loads(self.load_data())
            return self.data