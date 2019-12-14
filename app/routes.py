from flask import render_template
from flask import request
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/buy')
def buy():
    sellers=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]
    return render_template('buy.html',len=len(sellers),sellers=sellers)

@app.route('/send-request',methods=['GET', 'POST'])
def send_request():
    seller_data=request.form.to_dict()
    return render_template('send-request.html',data=seller_data)
    

@app.route('/sell')
def sell():
    return render_template('sell.html')

@app.route('/requests')
def requests():
    requests=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]
    return render_template('requests.html',len=len(requests),requests=requests)
