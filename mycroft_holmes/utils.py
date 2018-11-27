"""
Utility functions
"""


def format_query(query, params=None):
    """
    Replaces "{foo}" in query with values from params.
    Works just like Python str.format

    :type query str
    :type params dict
    :rtype: str
    """
    if params is None:
        return query

    for key, value in params.items():
        query = query.replace('{%s}' % key, value)

    return query


def yaml_variables_subst(yaml_raw, variables=None):
    """
    Performs variables substitute on a provided raw YAML content

    :type yaml_raw str
    :type variables dict
    :rtype:str
    """
    if variables is None:
        return yaml_raw

    # replace "${VAR_NAME}"
    for key, value in variables.items():
        yaml_raw = yaml_raw.replace('${%s}' % key, value)

    return yaml_raw
