"""
Provides a blueprint that renders JSON with software version and environment details
"""
from csv import DictWriter
from io import StringIO

from flask import Blueprint, jsonify, render_template, url_for, abort, make_response

from mycroft_holmes.app.utils import get_config, get_feature_spec_by_id
from mycroft_holmes.storage import MetricsStorage

from .models import get_components_with_metrics


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

            # feature's metadata
            'name': feature_name,
            'docs': feature_spec.get('url'),
            'repo': feature_spec.get('repo'),

            # fetch metrics and calculated score
            'metrics': [
                metric.get_label_with_value() for metric in metrics if metric.value is not None
            ],
            'score': storage.get(feature_id, feature_metric='score'),

            # link to a feature's dashboard
            'url': url_for('dashboard.feature', feature_id=feature_id),
        }

        components.append(component)

    # sort components by score (descending)
    components = sorted(components, key=lambda item: item['score'], reverse=True)

    # print(components)

    return render_template(
        'index.html',
        components=components,
        _json=url_for('dashboard.index_json'),
        _csv=url_for('dashboard.index_csv'),
    )


@dashboard.route('/index.json')
def index_json():
    """
    :rtype: flask.Response
    """
    components = get_components_with_metrics(config=get_config())

    features = []

    for component in components:
        component['metrics'] = {
            metric.get_name(): metric.value for metric in component['metrics']
        }

        component['links'] = {
            'self': url_for('dashboard.feature', feature_id=component['id'])
        }

        features.append(component)

    return jsonify(features)


@dashboard.route('/index.csv')
def index_csv():
    """
    :rtype: flask.Response
    """
    components = get_components_with_metrics(config=get_config())

    # get the unique list of all metric name
    metrics = set()

    for component in components:
        for metric in component['metrics']:
            metrics.add(metric.get_name())

    metrics = sorted(list(metrics))

    # https://docs.python.org/3.6/library/csv.html#writer-objects
    output = StringIO()

    csv = DictWriter(
        f=output,
        fieldnames=['Component', 'Documentation', 'Repository', 'Dashboard', 'Score'] + metrics
    )

    csv.writeheader()

    # write CSV rows
    for component in components:
        row = {
            'Component': component['name'],
            'Documentation': component['docs'],
            'Repository': component['repo'],
            'Dashboard': component['url'],
            'Score': component['score'],
        }

        for metric in component['metrics']:
            row[metric.get_name()] = metric.value

        csv.writerow(row)

    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/plain'

    return resp


@dashboard.route('/component/<string:feature_id>')
def feature(feature_id):
    """
    :type feature_id str
    :rtype: flask.Response
    """
    config = get_config()
    storage = MetricsStorage(config=config)

    # find a feature by ID
    feature_spec = get_feature_spec_by_id(config, feature_id)

    # not found? return 404
    if feature_spec is None:
        abort(404, 'Feature "%s" not found' % (feature_id,))

    metrics = [
        {
            'name': metric.get_name(),
            'icon': get_icon_for_source(metric.get_source_name()),
            'source': metric.get_source_name(),
            'raw_value': metric.value,
            'value': metric.get_formatted_value(),
            'weight': metric.get_weight(),
            'label': metric.get_label(),
            'more_link': metric.get_more_link(),
        }
        for metric in config.get_metrics_for_feature(feature_spec['name'])
    ]

    return render_template(
        'feature.html',
        component=feature_spec,
        metrics=metrics,
        score=storage.get(feature_id, feature_metric='score'),
        _csv='#',
        _json='#',
    )


def get_icon_for_source(source_name, default='extension'):
    """
    :type source_name str
    :type default str
    :rtype: str
    """
    # https://material.io/tools/icons/?style=baseline
    if source_name == 'wikia/jira':
        return 'bug_report'

    if source_name == 'wikia/analytics':
        return 'trending_up'

    return default
