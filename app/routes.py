from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/buy')
def buy():
<<<<<<< HEAD
    sellers=[{"Name":"abc","CarbonCredits":10},{"Name":"def","CarbonCredits":20},{"Name":"xyz","CarbonCredits":50}]
    return render_template('buy.html',len=len(sellers),sellers=sellers)

@app.route('/send-request')
def send_request(data):
    print(seller)
    return render_template('send-request.html',seller=data)
=======
    return render_template('buy.html')

@app.route('/sell')
def sell():
    return render_template('sell.html')
>>>>>>> 8375a9b06387511086f4dbb1ada6c5773cc3c9d7
