import json
import requests

from utilities.hash_util import hash_block
from utilities.verification import Verification
from block import Block
from transaction import Transaction
from node import Node

class Blockchain:
    def  __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self. node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('data/blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                # Reading File
                file_content = f.readlines()
                # Getting BlockChain form file
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['nodeId'], tx['candidateId'], tx['partyId'], tx['signature']) for tx in block['transactions']]
                    updated_block = Block(block['index'],  block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.__chain = updated_blockchain
                # Getting open transaction from file
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['nodeId'], tx['candidateId'], tx['partyId'], tx['signature'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                # Getting peer node from file
                peer_nodes = json.loads(file_content[2])       
                self.__peer_nodes = set(peer_nodes)
        except (IOError,IndexError):
            pass

    def save_data(self):
        try:
            with open('data/blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                # Saving Blockchain to file
                saveable_chain = [
                    block.__dict__ for block in [
                        Block(
                            block_el.index, 
                            block_el.previous_hash, 
                            [
                                tx.__dict__ for tx in block_el.transactions
                            ], 
                            block_el.proof, 
                            block_el.timestamp
                        ) for block_el in self.__chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                # Saving open transactions to file
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                # Saving peer nodes to file
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving Error!!')

    def proof_of_work(self): 
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not (Verification.valid_proof(self.__open_transactions, last_hash, proof)):
            proof += 1
        return proof

    def check_voter_validity(self):
        return True

    def count_votes(self):
        if(self.public_key == None):
            return None
        node_key = self.public_key
        tx_node = [[1 for tx in block.transactions if tx.nodeId == node_key] for block in self.__chain]
        open_tx_node = [[1] for tx in self.__open_transactions if tx.nodeId == node_key]
        tx_node.extend(open_tx_node)
        total_votes = 0
        for tx in tx_node:
            if(len(tx) > 0):
                total_votes += sum(tx)
        return total_votes

    def get_last_blockchain_value(self):
        if(len(self.__chain) < 1):
            return None
        return self.__chain[-1]

    def add_transaction(self, nodeId, candidateId, partyId, signature, is_recieving=False):
        
        transaction = Transaction(nodeId, candidateId, partyId, signature)
        if(Verification.verify_transaction(transaction, self.check_voter_validity)):
            self.__open_transactions.append(transaction)
            self.save_data()
            if(not is_recieving):
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'nodeId':nodeId, 'candidateId':candidateId, 'partyId':partyId, 'signature':signature})
                        if(response.status_code == 400 or response.status_code == 500):
                            print('Transaction declined, need resolving.')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False
            
    def mine_block(self):
        if(self.public_key == None):
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        copied_transactions = self.__open_transactions[:]   
        for tx in copied_transactions:
            if not (Node.verify_transaction(tx)):
                return None
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if(response.status_code == 400 or response.status_code == 500):
                    print('Block declined, need resolving.')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self,block):
        transactions = [Transaction(tx['nodeId'], tx['candidateId'], tx['partyId'], tx['signature']) for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions, block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.get_chain()[-1]) ==  block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transaction = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transaction:
                if( (opentx.nodeId == itx['nodeId']) and (opentx.candidateId == itx['candidateId']) and (opentx.partyId == itx['partyId']) and (opentx.signature == itx['signature'])):
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True
    
    def resolve(self):
        winner_chain = self.__chain
        replace = False
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [
                    Block(
                        block['index'], 
                        block['previous_hash'], 
                        [
                            Transaction(
                                tx['nodeId'], 
                                tx['candidateId'], 
                                tx['partyId'],
                                tx['signature'] 
                            ) for tx in block['transactions']
                        ], 
                        block['proof'], 
                        block['timestamp']
                    ) for block in node_chain
                ]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if(node_chain_length > local_chain_length and Verification.verify_chain(node_chain)):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.__chain = winner_chain
        if(replace):
            self.__open_transactions = []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)