from flask import Flask, request, jsonify
import os, sys
from core.model import Model

DB_PORT = os.environ['DB_PORT'] if 'DB_PORT' in os.environ else None
DB_HOST = os.environ['DB_HOST'] if 'DB_HOST' in os.environ else None
DB_NAME = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else None

app = Flask(__name__)

@app.route('/<int:time_range>')
def main(time_range):
    m = Model(DB_PORT,DB_HOST,DB_NAME)
    
    return jsonify(m.predict(time_range))
