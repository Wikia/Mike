"""
Provides a blueprint that renders JSON with software version and environment details
"""
from flask import Blueprint, jsonify

from mycroft_holmes.app.utils import get_config
from mycroft_holmes.storage import MetricsStorage

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/index.json')
def index_json():
    """
    :rtype: flask.Response
    """
    config = get_config()
    storage = MetricsStorage(config=config)

    return jsonify({
        'dashboard_name': config.get_name(),
        'features': [
            {
                'name': feature_name,
                'url': feature_spec.get('url'),
                'repo': feature_spec.get('repo'),
                'metrics': [metric['name'] for metric in feature_spec['metrics']],
                'score': storage.get(
                    feature_id=config.get_feature_id(feature_name),
                    feature_metric='score'
                ),
                'links': {
                    'self': None
                }
            }
            for feature_name, feature_spec in config.get_features().items()
        ]
    })
