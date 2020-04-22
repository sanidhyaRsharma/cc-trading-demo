from flask import render_template, request, flash, redirect, url_for
from functools import wraps
from app import app
import time
from .contract_abi import abi
from web3 import Web3, HTTPProvider
from Crypto.Hash import SHA256
import os, json
from .config import *
Session = {}

w3 = Web3(HTTPProvider('http://localhost:7545'))
contract = w3.eth.contract(address=CONTRACT_ADDR, abi = abi)

data_store = {}
purchase_request_store={}
user_store = {}
tx_history = {}

# functions to update JSON files which mock the databases
def initialize_file(file_name):
    filesize = os.path.getsize(file_name)

    if filesize == 0:
        return {}
    else: 
        with open(file_name, 'r') as filep:
            return json.load(filep)

# functions to update JSON files which mock the databases
def update_file(file_name, variable):
    with open(file_name, 'w') as filep:
        json.dump(variable, filep)

user_store = initialize_file('user_store.json')
data_store = initialize_file('data_store.json')
purchase_request_store = initialize_file('purchase_request_store.json')
tx_history = initialize_file('tx_history.json')

def addCredits(certificate, owner, amount, ttl):
    print("Inside addCredit")
    nonce = w3.eth.getTransactionCount(WALLET_ADDRESS)
    txn_dict =contract.functions.addCredits(certificate, w3.toChecksumAddress(owner), int(amount), int(ttl)).buildTransaction({
        'nonce':nonce
    })
    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=WALLET_PRIVATE_KEY)
    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.getTransactionReceipt(result)
    count = 0

    while tx_receipt is None and count < 30:
        time.sleep(20)
        tx_receipt = w3.eth.getTransactionReceipt(result)
    
    if tx_receipt is None:
        return False, -1
    uuid = int(tx_receipt['logs'][0]['data'], 16)

    # update cc balance
    Session['balance'] = get_cc_balance()
    return True, uuid, tx_receipt['transactionHash'].hex()

def generate_hash(data):
    return SHA256.new(data).hexdigest()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in Session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORIZED! Login required')
            return redirect(url_for('login'))
    return wrap

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        wallet_address = request.form.get('wallet-address')
        user_store[username] = {'password':password, 'wallet_address':wallet_address}
        update_file('user_store.json', user_store)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':    
        username = request.form.get('username')
        print(username)
        if username is None:
            return render_template('page-login.html')
        print(user_store.keys(), username)
        if username not in user_store.keys():
            return """
                <h1>Incorrect username</h1>
            """
        if(user_store[username]['password'] == request.form.get('password')):
            Session['username'] = username
            Session['logged_in'] = True
            Session['balance'] = get_cc_balance()
            return redirect(url_for('index'))
    return render_template('page-login.html')

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', notif="", ds = data_store, session=Session)

@app.route('/profile')
@login_required
def profile():
    return render_template('page-profile.html', username = Session['username'], wallet_address=user_store[Session['username']]['wallet_address'])

@app.route('/buy')
@login_required
def buy():
    # Prevent buying of self-owned carbon credits
    seller_dict = {}
    for key in data_store.keys():
        if key != user_store[Session['username']]['wallet_address']:
            seller_dict[key] = data_store[key]

    return render_template('buy.html',sellers=seller_dict, buyer=user_store[Session['username']], session=Session)

@app.route('/send-request',methods=['GET', 'POST'])
@login_required
def send_request():
    if request.method =='POST':
        # move entry to purchase_store
        seller_data = request.form.to_dict()
        print('seller_data:', seller_data)
        if seller_data['wallet-address'] in purchase_request_store.keys():
            purchase_request_store[seller_data['wallet-address']].append(seller_data)
        else:
            purchase_request_store[seller_data['wallet-address']] = [seller_data]

        # remove entry from data_store
        idx = 0
        for item in data_store[seller_data['wallet-address']]:
            print('item:', item)
            print('idx:', idx)
            print("seller_data['uuid']:", seller_data['uuid'])
            print("item['uuid']:", item['uuid'])
            if int(seller_data['uuid']) == int(item['uuid']):
                print('Inside if statement')
                current_obj = data_store[seller_data['wallet-address']].pop(int(idx))
                break
            idx += 1
        
        update_file('data_store.json', data_store)
        update_file('purchase_request_store.json', purchase_request_store)    
        return redirect(url_for('buy'))

    return render_template('send-request.html',data=seller_data, session=Session)
    

@app.route('/sell', methods=['GET','POST'])
@login_required
def sell():
    if user_store[Session['username']]['wallet_address'] != WALLET_ADDRESS:
        return """
            <h3>Access Denied</h3>
        """
    if request.method == 'POST':
        # INPUTS TO SMART CONTRACT addCredit
        # verified_certificate: string
        # address_of_owner: address
        # amount : uint256
        # ttl : seconds
        payload = {}
        payload['name_of_project'] = request.form.get('title')
        payload['reference_num'] = request.form.get('ref-num')
        payload['amount'] = request.form.get('amount')
        payload['time_period'] = request.form.get('time-period')
        addr = request.form.get('wallet-address')
        save_dir = os.path.join(os.getcwd(), 'xyz.pdf')

        # Save newly created Carbon Credit to blockchain
        try :
            with open(save_dir, "rb") as signed_doc:
                signed_doc_str = signed_doc.read()
                signed_doc_hash = generate_hash(signed_doc_str)
                result, uuid, tx_hash = addCredits(signed_doc_hash, addr, payload['amount'], int(payload['time_period'])*30*86400)
                if (result):
                    payload['uuid'] = uuid
                    if addr in data_store.keys():
                        data_store[addr].append(payload)
                    else:
                        data_store[addr] = [payload]
                    update_file('data_store.json', data_store)
                    # add transaction to transaction history
                    update_transaction_history(tx_hash, WALLET_ADDRESS, addr)
                    return render_template("index.html", notif = "Certificate added to blockchain", ds = data_store)
                else:
                    return render_template("index.html", notif = "Failed!2", ds= data_store)
        except Exception as e:
            print(e)
            return render_template("index.html", notif = "Failed!", ds= data_store)

    return render_template('sell.html', session=Session)

@app.route('/requests')
@login_required
def requests():
    requests = []
    key = user_store[Session['username']]['wallet_address']
 
    if key not in purchase_request_store.keys():
        print('No pending requests')
    else: 
        requests = purchase_request_store[user_store[Session['username']]['wallet_address']]
        print(requests)
        print(len(requests))

    return render_template('requests.html',len=len(requests),requests=requests, session=Session)


@app.route('/logout')
@login_required
def logout():
    Session.pop('logged_in')
    Session.pop('username')
    Session.pop('balance')

    return redirect(url_for('login'))

@app.route('/accept', methods=['GET','POST'])
@login_required
def accept():
    print('/accept is called')
    if request.method == "POST": 
        data =  request.get_json()
        # add transfer credits transaction to transaction history
        update_transaction_history(data['tx_hash'], data['from'], data['to'])

        # update view of requests and data_store
        current_obj = purchase_request_store[user_store[Session['username']]['wallet_address']].pop(int(data['i']))
        update_file('purchase_request_store.json', purchase_request_store)

        internal_dict = {'name_of_project': current_obj['name-of-project'], 
                        'reference_num': current_obj['reference-num'], 
                        'amount': current_obj['amount'],
                        'time_period': current_obj['time-period'],
                        'uuid': current_obj['time-period']}

        if current_obj['receiver-wallet-address'] in data_store.keys():
            data_store[current_obj['receiver-wallet-address']].append(internal_dict)
        else:
            data_store[current_obj['receiver-wallet-address']] = [internal_dict]

        update_file('data_store.json', data_store)

        # update cc balance
        Session['balance'] = get_cc_balance()

    return redirect(url_for('requests'))

# handler when purchase request of CC is rejected
@app.route('/reject/<index>')
@login_required
def reject(index):
    print('/reject is called')
    print('index :', index)
    current_obj = purchase_request_store[user_store[Session['username']]['wallet_address']].pop(int(index))
    update_file('purchase_request_store.json', purchase_request_store)

    return redirect(url_for('requests'))

# helper function used to convert wallet address to a username
def address_to_username(_address):
    for username in user_store.keys():
        if _address == user_store[username]['wallet_address']:
            return username
    
    return 'NONE'

def update_transaction_history(tx_hash, _from, _to):
    internal_dict = {}
    internal_dict['from'] = _from
    internal_dict['from_username'] = address_to_username(_from)
    internal_dict['to'] = _to
    internal_dict['to_username'] = address_to_username(_to)
    tx_history[tx_hash] = internal_dict
    update_file('tx_history.json', tx_history)
 
# global transaction history 
@app.route('/transaction_history')
def transaction_history():
    return render_template('transaction-history.html', transaction = tx_history)
 
# transaction history of a particular user
@app.route('/user_transaction_history')
@login_required
def user_transaction_history():
    user_transaction_history = {}
    current_user = user_store[Session['username']]['wallet_address']
    
    for key in tx_history.keys():
        if tx_history[key]['to'] == current_user or tx_history[key]['from'] == current_user:
            user_transaction_history[key] = tx_history[key]
 
    # no transaction made or received by user
    if user_transaction_history == {}:
        return render_template('blank-transaction-history.html')
    else:
        return render_template('transaction-history.html', transaction = user_transaction_history)
 
@login_required
def go_to_user_history():
    return redirect(url_for('user_transaction_history'))

def get_cc_balance():
    return str(contract.functions.viewCurrentBalance(user_store[Session['username']]['wallet_address']).call())