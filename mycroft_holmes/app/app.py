"""
This is an entry point for Mike's UI Flask-powered web-application
"""
# pylint: disable=no-member
import time
import os
from socket import gethostname

from flask import g, Flask

from mycroft_holmes import VERSION
from .utils import get_config

# import blueprints
from .blueprints import \
    dashboard,\
    version_info


# set up an app
def setup_app():
    """
    :rtype: Flask
    """
    # read the config
    get_config()

    app = Flask(__name__)
    app.logger.info('Starting Mycroft Holmes UI v%s', VERSION)

    # add blueprints
    app.register_blueprint(dashboard)
    app.register_blueprint(version_info)

    # various stuff
    app.context_processor(inject)
    app.before_request(app_before_request)
    app.after_request(app_after_request)

    return app


def inject():
    """
    Inject Mike's version, git commit hash and dashboard name
    :rtype: dict
    """
    return dict(
        dashboard_name=get_config().get_name(),
        version=VERSION,
        commit_hash=os.environ.get('COMMIT_SHA'),
    )


def app_before_request():
    """
    Measure response time
    """
    g.start = time.time()


hostname = gethostname()  # cache to avoid uname syscall on each request


def app_after_request(response):
    """
    :type response flask.wrappers.ResponseBase
    :rtype: flask.wrappers.ResponseBase
    """
    response.headers.set('X-Backend-Response-Time', '{:.4f}'.format(time.time() - g.start))
    response.headers.set('X-Served-By', hostname)

    return response
