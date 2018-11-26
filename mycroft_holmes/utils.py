"""
Utility functions
"""


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
