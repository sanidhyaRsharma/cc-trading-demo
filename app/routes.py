from flask import render_template, request, flash, redirect, url_for
from functools import wraps
from app import app
import time
from .contract_abi import abi
from web3 import Web3, HTTPProvider
from Crypto.Hash import SHA256
import os

Session = {}
'''
    Details of certifying auth
'''
CONTRACT_ADDR = '0xF2c77a25271ed0ACbc53132Aa00133F7ab7D4930'
WALLET_PRIVATE_KEY = '57ff5e0dab376a0d67bfd3009532df760d9c6496b261360f479200ed1264d0fb'
WALLET_ADDRESS = '0x8D031d67D5e904640994D3D541A70836c88dB3C3'

w3 = Web3(HTTPProvider('http://localhost:8545'))
# w3.eth.enable_unaudited_features()
contract = w3.eth.contract(address=CONTRACT_ADDR, abi = abi)

data_store = {}

user_store = {"abc@gmail.com": {'password': '12345', 'wallet_address':'0xE7b8F7F7E1ebBAb6588DA32ef3CEc78554Cf6aa6'},
              "un@unfdccc.com": {'password': 'qwerty', 'wallet_address': '0x33D6F007E249C1e6dfA0F23E0fDa9db8c0DbA3C0'}}

purchase_request_store={}

def addCredit(certificate, owner, amount, ttl):
    nonce = w3.eth.getTransactionCount(WALLET_ADDRESS)
    txn_dict =contract.functions.addCredit(certificate, w3.toChecksumAddress(owner), int(amount), int(ttl)).buildTransaction({
        'gas':3000000,
        'gasPrice':w3.eth.gasPrice,
        'nonce':nonce
    })
    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=WALLET_PRIVATE_KEY)
    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.getTransactionReceipt(result)
    count = 0

    while tx_receipt is None and count < 30:
        time.sleep(3)
        tx_receipt = w3.eth.getTransactionReceipt(result)
        print(tx_receipt)
    
    if tx_receipt is None:
        return False
    print(tx_receipt)
    return True

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
                if (addCredit(signed_doc_hash, addr, payload['amount'], int(payload['time_period'])*30*86400)):
                    if addr in data_store.keys():
                        data_store[addr].append(payload)
                    else:
                        data_store[addr] = [payload]
                    return render_template("index.html", notif = "Certificate added to blockchain", ds = data_store)
                else:
                    return render_template("index.html", notif = "Failed!", ds= data_store)
        except Exception as e:
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

@app.route('/reject', methods=['GET','POST'])
@login_required
def reject():
    print('/reject is called')
    if request.method == 'POST':
        data =  request.get_json()
        current_obj = purchase_request_store[user_store[Session['username']]['wallet_address']].pop(int(data['i']))
        print(current_obj)
    return redirect(url_for('requests'))