"""
ConstSource class
"""
from .base import SourceBase


class ConstSource(SourceBase):
    """
    Source that returns a constant value. Can be used to tweak a score of a feature.

    ### `metrics` config

    ```yaml
        metrics:
          -  name: common/const
             weight: 100
    ```
    """

    NAME = 'common/const'

    def get_value(self):
        return 1
