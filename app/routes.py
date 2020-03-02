from flask import render_template, request, flash, redirect, url_for
from functools import wraps
from app import app
import time
from .contract_abi import abi
from web3 import Web3, HTTPProvider
from Crypto.Hash import SHA256
import os, json

Session = {}
'''
    Details of certifying auth
'''
CONTRACT_ADDR = '0x091590dE64a68dC63502d9f674552ba00867D4a1'
WALLET_PRIVATE_KEY = '9c0a71e91e49c55a9bc537e5a61b015fc82c7fa4616b6daeb42d442933805349'
WALLET_ADDRESS = '0x33D6F007E249C1e6dfA0F23E0fDa9db8c0DbA3C0'

w3 = Web3(HTTPProvider('http://localhost:7545'))
# w3.eth.enable_unaudited_features()
contract = w3.eth.contract(address=CONTRACT_ADDR, abi = abi)

data_store = {}

user_store = {"company1@gmail.com": {'password': '12345', 'wallet_address':'0xe4D1E737a1D734F37Ec734D62791486f6EaaF469'},
              "un@unfdccc.com": {'password': 'qwerty', 'wallet_address': '0x33D6F007E249C1e6dfA0F23E0fDa9db8c0DbA3C0'},
              "company2@gmail.com": {'password': '12345', 'wallet_address':'0x296a34459D0B38D1ec759b31a5DdBd118D64978b'}}

with open('user_store.json', 'w') as filep:
    json.dump(user_store, filep)

with open('user_store.json', 'r') as filep:
    user_store = json.load(filep)

purchase_request_store={}

def addCredit(certificate, owner, amount, ttl):
    print("Inside addCredit")
    nonce = w3.eth.getTransactionCount(WALLET_ADDRESS)
    txn_dict =contract.functions.addCredits(certificate, w3.toChecksumAddress(owner), int(amount), int(ttl)).buildTransaction({
        'nonce':nonce
    })
    # event_filter = contract.events.
    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=WALLET_PRIVATE_KEY)
    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(result)
    tx_receipt = w3.eth.getTransactionReceipt(result)
    print(tx_receipt)
    count = 0

    while tx_receipt is None and count < 30:
        time.sleep(20)
        tx_receipt = w3.eth.getTransactionReceipt(result)
        print(tx_receipt)
    
    print(tx_receipt)

    if tx_receipt is None:
        return False, -1
    uuid = int(tx_receipt['logs'][0]['data'], 16)
    print(uuid)
    return True, uuid

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
        print(user_store)
        with open('user_store.json', 'w') as filep:
            json.dump(user_store, filep)
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
    # sellers=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]
    return render_template('buy.html',sellers=data_store, buyer=user_store[Session['username']], session=Session)

@app.route('/send-request',methods=['GET', 'POST'])
@login_required
def send_request():
    if request.method =='POST':
        seller_data = request.form.to_dict()
        if seller_data['wallet-address'] in purchase_request_store.keys():
            purchase_request_store[seller_data['wallet-address']].append(seller_data)
        else:
            purchase_request_store[seller_data['wallet-address']] = [seller_data]
        return redirect(url_for('index'))
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
        print(save_dir)
        print(request.files['certificate'].save(save_dir))
        # put certificate string in payload


        # Save newly created Carbon Credit to blockchain
        try :
            with open(save_dir, "rb") as signed_doc:
                signed_doc_str = signed_doc.read()
                print(type(signed_doc_str))
                signed_doc_hash = generate_hash(signed_doc_str)
                print(signed_doc_hash)
                result, uuid= addCredit(signed_doc_hash, addr, payload['amount'], int(payload['time_period'])*30*86400)
                print("CHECK", result, uuid)
                if (result):
                    payload['uuid'] = uuid
                    if addr in data_store.keys():
                        data_store[addr].append(payload)
                    else:
                        data_store[addr] = [payload]
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
    # requests=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]
    requests = purchase_request_store[user_store[Session['username']]['wallet_address']]
    print(requests)
    return render_template('requests.html',len=len(requests),requests=requests, session=Session)

@app.route('/logout')
@login_required
def logout():
    Session.pop('logged_in')
    Session.pop('username')
    return redirect(url_for('login'))

@app.route('/accept', methods=['GET','POST'])
@login_required
def accept():
    print('/accept is called')
    if request.method == "POST": 
        data =  request.get_json()
        print(data['i'])
        current_obj = purchase_request_store[user_store[Session['username']]['wallet_address']].pop(int(data['i']))
        curr_list = data_store[current_obj['wallet-address']]
        count = 0
        idx = 0
        for item in curr_list:
            if item['reference_num'] == current_obj['reference-num']:
                idx = count
            count+=1
        
        if current_obj['receiver-wallet-address'] in data_store.keys():
            data_store[current_obj['receiver-wallet-address']].append(data_store[current_obj['wallet-address']][idx])
        else:
            data_store[current_obj['receiver-wallet-address']] = [(data_store[current_obj['wallet-address']][idx])]
        data_store[current_obj['wallet-address']].pop(idx)
        return redirect(url_for('requests'))
    return redirect(url_for('requests'))

@app.route('/reject', methods=['GET','POST'])
@login_required
def reject():
    print('/reject is called')
    if request.method == 'POST':
        data =  request.get_json()
        current_obj = purchase_request_store[user_store[Session['username']]['wallet_address']].pop(int(data['i']))
        print(current_obj)
    return redirect(url_for('requests'))