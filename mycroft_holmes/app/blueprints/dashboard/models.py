"""
Models for accessing components and metrics data
"""
from flask import url_for

from mycroft_holmes.storage import MetricsStorage


def get_components_with_metrics(config):
    """
    :type: config mycroft_holmes.config.Config
    """
    storage = MetricsStorage(config=config)

    components = []

    for feature_name, feature_spec in config.get_features().items():
        feature_id = config.get_feature_id(feature_name)
        metrics = config.get_metrics_for_feature(feature_name)

        component = {
            'id': feature_id,

            # feature's metadata
            'name': feature_name,
            'docs': feature_spec.get('url'),
            'repo': feature_spec.get('repo'),

            # fetch metrics and calculated score
            'metrics': metrics,
            'score': storage.get(feature_id, feature_metric='score'),

            # link to a feature's dashboard
            'url': url_for('dashboard.feature', feature_id=feature_id, _external=True),
        }

        components.append(component)

    # sort components by score (descending)
    components = sorted(components, key=lambda item: item['score'], reverse=True)

    return components
