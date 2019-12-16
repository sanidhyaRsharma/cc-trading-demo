from flask import render_template, request, flash, redirect, url_for
from functools import wraps
from app import app
import time
from .contract_abi import abi
from web3 import Web3, HTTPProvider

Session = {}
CONTRACT_ADDR = '0x091590dE64a68dC63502d9f674552ba00867D4a1'
WALLET_PRIVATE_KEY = '9C0A71E91E49C55A9BC537E5A61B015FC82C7FA4616B6DAEB42D442933805349'
WALLET_ADDRESS = '0x33D6F007E249C1e6dfA0F23E0fDa9db8c0DbA3C0'

w3 = Web3(HTTPProvider('http://localhost:7545'))
# w3.eth.enable_unaudited_features()

contract = w3.eth.contract(address=CONTRACT_ADDR, abi = abi)

data_store = {}
user_store = {"abc@gmail.com": {'password': '12345', 'wallet_address':'0xe4D1E737a1D734F37Ec734D62791486f6EaaF469'},
              "un@unfdccc.com": {'password': 'qwerty', 'wallet_address': '0x33D6F007E249C1e6dfA0F23E0fDa9db8c0DbA3C0'}}

def addCredit(certificate, owner, amount, ttl):
    nonce = w3.eth.getTransactionCount(WALLET_ADDRESS)
    txn_dict =contract.functions.addCredit(certificate, w3.toChecksumAddress(owner), int(amount), int(ttl)).buildTransaction({
        'gas':2000000,
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
        wallet_address = request.form.get('wallet_address')
        user_store[username] = {'password':password, 'wallet_address':wallet_address}
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
    return render_template('index.html', notif="", ds = data_store)

@app.route('/buy')
@login_required
def buy():
    # sellers=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]

    return render_template('buy.html',sellers=data_store)

@app.route('/send-request',methods=['GET', 'POST'])
@login_required
def send_request():
    if request.method =='POST':
        seller_data = request.form.to_dict()
    return render_template('send-request.html',data=seller_data)
    

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
        payload['reference_num'] = request.form.get('ref_num')
        payload['amount'] = request.form.get('amount')
        payload['time_period'] = request.form.get('time-period')
        addr = request.form.get('wallet-address')

        # put certificate string in payload


        # Save newly created Carbon Credit to blockchain
        #TODO: replace testCertificateString with actual file
        if (addCredit("testCertificateString", addr, payload['amount'], int(payload['time_period'])*30*86400)):
            if addr in data_store.keys():
                data_store[addr].append(payload)
            else:
                data_store[addr] = [payload]
            return render_template("index.html", notif = "Certificate added to blockchain", ds = data_store)
        else:
            return render_template("index.html", notif = "Failed!", ds= data_store)


    return render_template('sell.html')

@app.route('/requests')
@login_required
def requests():
    requests=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]

    return render_template('requests.html',len=len(requests),requests=data_store)