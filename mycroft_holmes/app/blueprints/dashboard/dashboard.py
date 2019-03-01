"""
Provides a blueprint that renders JSON with software version and environment details
"""
from collections import defaultdict
from csv import DictWriter
from io import StringIO

import yaml

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
    components = get_components_with_metrics(config=config)
    storage = MetricsStorage(config=config)
    features = []

    for component in components:
        component['metrics'] = [
            metric.get_label_with_value() for metric in component['metrics']
        ]

        component['url'] = url_for('dashboard.feature', feature_id=component['id'])

        features.append(component)

    return render_template(
        'index.html',
        components=components,
        the_latest_timestamp=storage.get_the_latest_timestamp(),
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
            'self': url_for('dashboard.feature', feature_id=component['id'], _external=True),
            'yaml': url_for('dashboard.feature_yaml', feature_id=component['id'], _external=True),
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

    # render a spec as YAML
    spec_yaml = yaml.safe_dump(feature_spec, default_flow_style=False)

    return render_template(
        'feature.html',
        component=feature_spec,
        spec_yaml=spec_yaml,
        metrics=metrics,
        score=storage.get(feature_id, feature_metric='score'),
        the_latest_timestamp=storage.get_the_latest_timestamp(),
        _csv=url_for('dashboard.feature_csv', feature_id=feature_id),
        _json='#',
        _yaml=url_for('dashboard.feature_yaml', feature_id=feature_id),
    )


@dashboard.route('/component/<string:feature_id>.csv')
def feature_csv(feature_id):
    """
    :type feature_id str
    :rtype: flask.Response
    """
    config = get_config()
    feature_spec = get_feature_spec_by_id(config, feature_id)

    # not found? return 404
    if feature_spec is None:
        abort(404, 'Feature "%s" not found' % (feature_id,))

    # get all names of all metrics
    metrics = ['score'] + sorted([
        metric.get_name()
        for metric in config.get_metrics_for_feature(feature_spec['name'])
    ])

    storage = MetricsStorage(config=config)
    values = defaultdict(dict)

    # "merge" different metrics from the same day into CSV per-day rows
    for row in storage.get_feature_metrics_history(feature_id):
        date = str(row['date'])
        metric_name = row['metric']
        metric_value = row['value']

        # avoid: ValueError: dict contains fields not in fieldnames: 'analytics/events'
        if metric_name in metrics:
            values[date][metric_name] = metric_value

    # https://docs.python.org/3.6/library/csv.html#writer-objects
    output = StringIO()

    csv = DictWriter(
        f=output,
        fieldnames=['date'] + metrics
    )

    csv.writeheader()

    # write CSV rows
    for date, row in values.items():
        row.update({"date": date})
        csv.writerow(row)

    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/plain'

    return resp


@dashboard.route('/component/<string:feature_id>.yaml')
def feature_yaml(feature_id):
    """
    :type feature_id str
    :rtype: flask.Response
    """
    config = get_config()

    # find a feature by ID
    feature_spec = get_feature_spec_by_id(config, feature_id)

    # render a spec as YAML
    spec_yaml = yaml.safe_dump(feature_spec, default_flow_style=False)

    # serve as a plain text
    resp = make_response(spec_yaml)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


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
