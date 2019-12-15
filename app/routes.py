from flask import render_template, request
from app import app
import time
from web3 import Web3, HTTPProvider

contract_address = 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/buy')
def buy():
    return render_template('buy.html')

@app.route('/sell', methods=['GET','POST'])
def sell():
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
        #put certificate string in payload
        
    return render_template('sell.html')