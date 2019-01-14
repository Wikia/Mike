"""
This is an entry point for Mike's UI Flask-powered web-application
"""
# pylint: disable=no-member
from flask import Flask

from mycroft_holmes import VERSION
from .utils import get_config

# import blueprints
from .blueprints import version_info


# read the config
get_config()

# set up an app
app = Flask(__name__)
app.logger.info('Starting Mycroft Holmes UI v%s', VERSION)

# add blueprints
app.register_blueprint(version_info)
