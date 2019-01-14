"""
Provides a blueprint that renders JSON with software version and environment details
"""
from flask import Blueprint, jsonify, render_template, url_for

from mycroft_holmes.app.utils import get_config
from mycroft_holmes.storage import MetricsStorage

dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.route('/')
def index():
    """
    :rtype: flask.Response
    """
    config = get_config()
    storage = MetricsStorage(config=config)

    components = []

    for feature_name, feature_spec in config.get_features().items():
        feature_id = config.get_feature_id(feature_name)
        metrics = config.get_metrics_for_feature(feature_name)
        # print(feature_name, metrics)

        component = {
            'id': feature_id,

            'name': feature_name,
            'url': feature_spec.get('url'),
            'repo': feature_spec.get('repo'),

            'metrics': [
                metric.get_label_with_value() for metric in metrics if metric.value is not None
            ],
            'score': storage.get(feature_id, feature_metric='score'),
        }

        components.append(component)

    # sort components by score (descending)
    components = sorted(components, key=lambda item: item['score'], reverse=True)

    print(components)

    return render_template(
        'index.html',
        dashboard_name=config.get_name(),
        components=components,
        _json=url_for('dashboard.index_json'),
    )


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
                    'self': url_for('dashboard.index')
                }
            }
            for feature_name, feature_spec in config.get_features().items()
        ]
    })
