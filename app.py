from flask import Flask, request, jsonify
import os, sys
from core.model import Model

API_KEY = os.environ['API_KEY'] if 'API_KEY' in os.environ else None

app = Flask(__name__)

@app.route('/<int:time_range>')
def main(time_range):
    m = Model(API_KEY)
    
    return jsonify(m.predict(time_range))
