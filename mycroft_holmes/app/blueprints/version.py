"""
Provides a blueprint that renders JSON with software version and environment details
"""
import sys
import socket

from flask import Blueprint, jsonify

from mycroft_holmes import VERSION
from ..utils import get_config

version_info = Blueprint('version', __name__)


@version_info.route('/version.json')
def version():
    """
    :rtype: flask.Response
    """
    return jsonify({
        'python_version': sys.version,
        'mike_host': socket.gethostname(),
        'mike_version': VERSION,
        'dashboard_name': get_config().get_name()
    })
