from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

class Node:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()

    def save_keys(self):
        if(self.public_key != None and self.private_key != None):
            try:
                with open('data/node-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving node failed...')
                return False


    def load_keys(self):
        try:
            with open('data/node-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                self.public_key, self.private_key = keys[0][:-1], keys[1]
            return True
        except (IOError, IndexError):
            print('Loading node failed...')
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