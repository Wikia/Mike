"""
This is an entry point for Mike's UI Flask-powered web-application
"""
import sys
import socket

from flask import Flask, jsonify

from mycroft_holmes import VERSION

app = Flask(__name__)


@app.route("/version.json")
def hello():
    return jsonify({
        'python_version': sys.version,
        'mike_host': socket.gethostname(),
        'mike_version': VERSION,
    })
