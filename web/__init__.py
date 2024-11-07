import json
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

CORS(app, resources={r"/*": {"origins": "*"}})

from web.controller import *
