from bottle import Bottle, request, route
import json
import time
import datetime
import hashlib

app = Bottle(__name__)

# Store the transactions that
# this node has in a list
this_nodes_transactions = []

miner_address = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()

print("\n\nMiner Address:", miner_address, '\n\n')

all_accounts = []

blockchain = []

def Block(index, timestamp, data, prev_hash):
    hash_data = hashlib.sha256((str(index) + str(timestamp) + str(data) + str(prev_hash)).encode('utf-8')).hexdigest()

    return {'index': index, 'timestamp': str(timestamp), 'data': data, 'prev_hash': prev_hash, 'hash': hash_data}

def proof_of_work(last_proof):
  # Create a variable that we will use to find
  # our next proof of work
  incrementor = last_proof + 1
  # Keep incrementing the incrementor until
  # it's equal to a number divisible by 9
  # and the proof of work of the previous
  # block in the chain
  while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
    incrementor += 1
  # Once that number is found,
  # we can return it as a proof
  # of our work
  return incrementor

@app.route('/new')
def account():
  new_address = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
  
  all_accounts.append(new_address)

  return {'status': 'Success', 'address': new_address}

@app.route('/accounts')
def accounts():
  return {'status': 'Success', 'accounts': all_accounts}

@app.route('/genesis_block')
def genesis_block():
    if(len(blockchain) == 0):
        block = Block(0,datetime.datetime.now(),{'transactions': [], 'proof-of-work': 1},'0')
        #block = {'index': 0, 'data':{'transactions': [], 'proof-of-work': 1}, 'hash': '', 'timestamp': date.datetime.now()}
        blockchain.append(block)
        return {'status': 'Genesis Block Created', 'blockchain': blockchain}
    else:
        return 'Genesis Exists'

@app.route('/txn')
def transaction():

  from_addr = request.GET.get('f')
  to_addr = request.GET.get('t')
  amount = request.GET.get('a')
  data = request.GET.get('d')
  
  new_txion = {'from': from_addr, 'to': to_addr, 'amount': amount, 'data': data}
  # Then we add the transaction to our list
  this_nodes_transactions.append(new_txion)
  
  return {'status': 'Success', 'transaction': new_txion}

@app.route('/mine')
def mine():
  if(len(blockchain) == 0):
    return {'status': 'Genesis Does Not Exist :('}
  # Get the last proof of work
  last_block = blockchain[len(blockchain) - 1]
  # print(last_block)
  last_proof = last_block['data']['proof-of-work']
  # Find the proof of work for
  # the current block being mined
  # Note: The program will hang here until a new
  #       proof of work is found

  proof = proof_of_work(last_proof)
  # Once we find a valid proof of work,
  # we know we can mine a block so 
  # we reward the miner by adding a transaction
  this_nodes_transactions.append(
    { "from": "network", "to": miner_address, "amount": 1, "data": "Network reward!" }
  )
  # Now we can gather the data needed
  # to create the new block
  new_block_data = {
    "proof-of-work": proof,
    "transactions": list(this_nodes_transactions)
  }
  new_block_index = last_block['index'] + 1
  new_block_timestamp = this_timestamp = datetime.datetime.now()
  last_block_hash = last_block['hash']
  # Empty transaction list
  this_nodes_transactions[:] = []
  # Now create the
  # new block!
  mined_block = Block(
    new_block_index,
    new_block_timestamp,
    new_block_data,
    last_block_hash
  )
  blockchain.append(mined_block)
  # Let the client know we mined a block
  return {'status': 'Success', 'new_block': {
      "index": new_block_index,
      "timestamp": str(new_block_timestamp),
      "data": new_block_data,
      "hash": last_block_hash
}}

@app.route('/blocks', methods=['GET'])
def get_blocks():
  chain_to_send = blockchain
  return {'status': 'Success', 'blockchain': chain_to_send}