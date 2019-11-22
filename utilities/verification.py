from utilities.hash_util import hash_string_256,hash_block
from node import Node
from bson.json_util import loads
from bson.json_util import dumps


class Verification:
    
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            if(index == 0):
                continue
            if(block.previous_hash != hash_block(blockchain[index -1])):
                return False
            if not cls.valid_proof(block.transactions, block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False 
        return True

    @staticmethod
    def verify_transaction(transaction, check_voter_validity, check_validity=True):
        if(check_validity):
            return check_voter_validity and Node.verify_transaction(transaction)
        else:
            return Node.verify_transaction(transaction)

class Initialiser:

    @staticmethod
    def scan_card():
        '''Card Scanning dummy Logic for System Initialization'''
        return int(input('Enter 6-digit Card Secret: '))

class Authentication:

    @staticmethod
    def authenticate(scannedId, node):
        allVoters = loads(node.data)[0]['Voters']
        validity = 0
        voterData = ''
        for entry in allVoters:
            if(scannedId == entry['VoterId']):
                validity = 1
                voterData = dumps(entry)
        if(validity == 0):
            voterData = 'NA'
        return (validity,voterData)