"""
ConstSource class
"""
from .base import SourceBase


class ConstSource(SourceBase):
    """
    Returns a constant value (can be used to tweak a score of a feature).

    ### `metrics` config

    ```yaml
        metrics:
          -  name: common/const
             weight: 100
    ```
    """

    NAME = 'common/const'

    def get_value(self, **kwargs):
        return 1
