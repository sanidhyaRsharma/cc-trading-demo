from flask import Flask

app = Flask(__name__)
app.secret_key = 'this_is_a_secret'
from app import routes