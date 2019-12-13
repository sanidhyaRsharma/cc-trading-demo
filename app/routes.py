from flask import render_template, request
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/buy')
def buy():
    return render_template('buy.html')

@app.route('/sell', methods=['GET','POST'])
def sell(req):
    
    return render_template('sell.html')