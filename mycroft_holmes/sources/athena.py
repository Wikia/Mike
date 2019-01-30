"""
AWS Athena class
"""
from pyathena import connect

from .base import DatabaseSourceBase


class AthenaSource(DatabaseSourceBase):
    """
    Returns a number result for a given SQL query run on AWS Athena.

    https://aws.amazon.com/athena/

    #### `sources` config

    ```yaml
    sources:
      - name: foo/athena
        kind: aws/athena
        access_key_id: "${ATHENA_ACCESS_KEY_ID}"
        secret_access_key: "${ATHENA_SECRET}"
        s3_staging_dir: "${ATHENA_S3_STAGING_DIR}"
        region: "us-east-1"
    ```

    > `s3_staging_dir` is the S3 location to which your query output is written,
    for example `s3://query-results-bucket/folder/`, which is established under Settings
    in the [Athena Console](https://console.aws.amazon.com/athena/).

    #### `metrics` config

    ```yaml
        metrics:
          - name: foo/wikis
            source: foo/athena
            query: "SELECT count(*) FROM stats.wikis WHERE lang = %(wiki_lang)s"
            label: "{wiki_lang} wikis count: %d"
    ```

    Please note that only the first column from the first row in the results set will be taken.

    #### `features` config

    ```yaml
        features:
          - name: Wikis
            template:
              - wiki_lang: "is"  # this will be used in query defined above
            metrics:
              -  name: foo/wikis
    ```
    """

    NAME = 'aws/athena'

    # pylint: disable=too-many-arguments
    def __init__(self, access_key_id, secret_access_key, s3_staging_dir, region, client=None):
        """
        :type access_key_id str
        :type secret_access_key str
        :type s3_staging_dir str
        :type region str
        :type client obj
        """
        super(AthenaSource, self).__init__()

        self._connection_params = dict(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            s3_staging_dir=s3_staging_dir,
            region_name=region
        )

        self._client = client or None

    def _get_client(self):
        """
        Connect to Athena lazily

        :rtype: mysql.connector.connection.MySQLConnection
        """
        self.logger.info('Connecting to Athena in "%s"...',
                         self._connection_params['region_name'])

        # https://pypi.org/project/PyAthena/
        return  connect(**self._connection_params)
