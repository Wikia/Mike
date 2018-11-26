"""
Set of unit test for variables substitution
"""
from mycroft_holmes.utils import yaml_variables_subst

YAML = """
foo: "${FOO}"
bar: "FOO"
""".strip()


def test_subst():
    assert yaml_variables_subst(YAML) == YAML, 'No-op when no variables were provided'
    assert yaml_variables_subst(YAML, variables={'foo': 'var'}) == YAML, 'No-op when no variable matches'

    assert 'foo: "VAR"' in yaml_variables_subst(YAML, variables={'FOO': 'VAR'})
