from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from utilities.verification import Initialiser
from utilities.verification import Authentication
from node import Node
from blockchain import Blockchain
import socket
import pickle as pk
from bson.json_util import loads
from bson.json_util import dumps

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')

@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')

@app.route('/profile', methods=['GET'])
def get_profile_ui():
    return send_from_directory('ui', 'profile.html')

@app.route('/vote', methods=['GET'])
def get_vote_ui():
    return send_from_directory('ui', 'voting.html')

@app.route('/results', methods=['GET'])
def get_result_ui():
    return send_from_directory('ui', 'results.html')

@app.route('/node', methods=['POST'])
def create_node():
    node.create_keys()
    if(node.save_keys()):
        global blockchain
        blockchain = Blockchain(node.public_key, port)
        response = {
            'public_key': node.public_key,
            'private_key': node.private_key,
            'votes': blockchain.count_votes(),
            'node_id': node.node_id
        }
        return jsonify(response), 201
    else:
        response = {
        'message': 'Saving the keys failed'
        }
        return jsonify(response), 500

@app.route('/node', methods=['GET'])
def load_node():
    if(node.load_keys()):
        global blockchain
        blockchain = Blockchain(node.public_key, port)
        response = {
            'public_key': node.public_key,
            'private_key': node.private_key,
            'votes': blockchain.count_votes(),
            'node_id': node.node_id
        }
        return jsonify(response), 201
    else:
        response = {
        'message': 'Keys not available.'
        }
        return jsonify(response), 500

@app.route('/votes', methods=['GET'])
def get_votes():
    total_votes = blockchain.count_votes()
    if(total_votes != None):
        response = {
            'message': 'Fetched total_votes successfully.',
            'votes': total_votes
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed',
            'wallet_set_up': node.public_key != None
        }
        return jsonify(response), 500

@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if(not values):
        response = {'message':'No data found.'}
        return jsonify(response), 400
    required_fields = ['nodeId', 'candidateId', 'partyId', 'signature']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data missing.'
        }
        return jsonify(response), 400
    success = blockchain.add_transaction(values['nodeId'], values['candidateId'], values['partyId'], values['signature'], is_recieving=True)
    if(success):
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'nodeId': values['nodeId'],
                'candidateId': values['candidateId'],
                'partyId': values['partyId'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creation of transaction failed.'
        }
        return jsonify(response), 500

@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if(not values):
        response = {'message':'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Required data missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.get_chain()[-1].index + 1:
        if(blockchain.add_block(block)):
            response = {'message': 'Block added.'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.get_chain()[-1].index:
        response = {'message':'Blockchain seems to be differ from local blockchain'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {'message':'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409

@app.route('/transaction', methods=['POST']) 
def add_transaction():
    if(node.public_key == None):
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if(not values):
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['candidateId', 'partyId']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data missing.'
        }
        return jsonify(response), 400
    candidateId = values['candidateId']
    partyId = values['partyId']
    signature = node.sign_transaction(node.public_key, candidateId, partyId)
    success = blockchain.add_transaction(node.public_key, candidateId, partyId, signature)
    if(success):
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'nodeId': node.public_key,
                'candidateId': candidateId,
                'partyId': partyId,
                'signature': signature
            },
            'votes': blockchain.count_votes()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creation of transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if(blockchain.resolve_conflicts == True):
        response = {'message':'Resolve conflicts first, block not added!'}
        return jsonify(response), 500
    block = blockchain.mine_block()
    if(block != None):
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added sucessfully',
            'block': dict_block,
            'votes': blockchain.count_votes()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed',
            'node_set_up': node.public_key != None
        }
        return jsonify(response), 500

@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if(replaced):
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.get_chain()
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200

@app.route('/peer', methods=['POST'])
def add_peer():
    values = request.get_json()
    if not (values):
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if('peer' not in values):
        response = {
            'message': 'No peer data found.'
        }
        return jsonify(response), 400
    peer = values['peer']
    blockchain.add_peer_node(peer)
    response = {
        'message': 'Peer added successfully.',
        'all_peers': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201
         
@app.route('/peer/<peer_url>', methods=['DELETE'])
def remove_peer(peer_url):
    if(peer_url == '' or peer_url == None):
        response = {
            'message': 'No peer found.'
        }
        return jsonify(response), 400 
    blockchain.remove_peer_node(peer_url)
    response = {
        'message': 'Peer removed.',
        'all_peers': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200 

@app.route('/peer', methods=['GET'])
def get_peers():
    peers = blockchain.get_peer_nodes()
    response = {
        'all_peers': peers
    }
    return jsonify(response), 200 

@app.route('/data', methods=['GET'])
def send_data():
    response = {
        'constituencyData': dumps(loads(node.data)[0])
    }
    return jsonify(response), 200

@app.route('/authenticate', methods=['POST'])
def authenticate_voter():
    values = request.get_json()
    scannedId = values['scannedId']
    validity, voterData = Authentication.authenticate(scannedId, node)
    response = {
        'validVoter' : validity,
        'voterData': voterData
    }
    return jsonify(response), 200

@app.route('/mark-attendence', methods=['POST'])
def mark_voter_attendence():
    values = request.get_json()
    roll_no = values['attendenceRollNo']
    mark = node.mark_attendence(roll_no)
    response = {
        'marked': mark
    }
    return jsonify(response), 200

@app.route('/upload-attendence', methods=['POST'])
def upload_attendence():
    attendedVoters = loads(node.data)[0]['Voters']
    ConstId = loads(node.data)[0]['ConstId']
    s = socket.socket()
    s.connect(('localhost', 12345))
    s.send('upload'.encode())
    print(s.recv(1024).decode())
    s.send(pk.dumps((ConstId,attendedVoters)))
    serverResponse = s.recv(1024).decode()
    s.close()
    response = {
        'serverResponse': serverResponse
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-m', '--mode', type=str, default='initialize')
    args = parser.parse_args()
    port = args.port
    mode = args.mode
    if(mode == 'initialize'):
        print('\n'+(5*'=')+'System Initalization'+(5*'='))
        print('\nPlease Scan constituency smart card...')
        secret = Initialiser.scan_card()
    elif(mode == 'restart'):
        secret = 'NA'
    node = Node(port, secret)
    blockchain = Blockchain(node.public_key, port)
    app.run(host='0.0.0.0', port=port, debug=True)