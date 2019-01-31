Sources
=======

This directory contains implementation of various sources that provide values for metrics.

## Vocabulary

* **`source`** is a data provider. It can be a MySQL database, Google Analytics API, elasticsearch or your JIRA instance. Each source needs to be set up with an instance specific configuration (e.g. MySQL credentials, elasticsearch host address).
* **`metric`** defines a query on a specific `source`. It can perform a defined SQL query on MySQL database, get events count from Google Analytics or count JIRA tickets matching a given JQL. Metric returns a specific value.
* **`feature`** is a set of `metrics`. They are used to calculate feature's score. Each feature can provide a set of "template" variables that are passed to `metrics` to customize their queries run against `sources`.

> Please refer to sources documentation below and to `test/fixtures/config.yaml` for more examples.

## Available sources

* `aws/athena`: Returns a number result for a given SQL query run on AWS Athena.
* `common/analytics`: Returns a metric value from Google Analytics.
* `common/const`: Returns a constant value (can be used to tweak a score of a feature).
* `common/jira`: Returns a number of Jira ticket matching given JQL query.
* `common/logstash`: Returns a number of entries matching a given elasticsearch query.
* `common/mysql`: Returns a number result for a given SQL query.

### TODO

#### Wikia-specific sources

* `wikia/wikifactory` (queries WikiFactory database that is used to configure every wiki Wikia hosts)

### AthenaSource

Source name: `aws/athena`

> Returns a number result for a given SQL query run on AWS Athena.

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

### GoogleAnalyticsSource

Source name: `common/analytics`

> Returns a metric value from Google Analytics.

#### `sources` config

```yaml
sources:
  - name: foo/analytics
    kind: common/analytics
    # JSON-encoded string with service account credentials
    credentials: '${ANALYTICS_SERVICE_ACCOUNT_JSON}'
    view_id: 1234  # your Google Analytics view ID
```

**JSON key file** (you will use it as `credentials` config key) generation guide:
https://flaviocopes.com/google-api-authentication/#service-to-service-api

* "Google Analytics Reporting API" needs to be enabled for service account.
* You need to add an email (specified in service account JSON file) to your GA users.

> See https://github.com/Wikia/Mike/issues/12 for more details and troubleshooting guides.

Please note that currently Mike does not support storing float values.
Metrics like `ga:bounceRate` will be casted to an integer.

#### `metrics` config

```yaml
    metrics:
      # Google Analytics
      - name: analytics/events
        source: foo/analytics
        label: "%d GA events"
        # https://developers.google.com/analytics/devguides/reporting/core/dimsmets
        metric: "ga:totalEvents"
        filters: "{ga_filter}"  # this is optional
```

#### `features` config

```yaml
    features:
      - name: FooBar
        template:
          - ga_filter: "ga:eventCategory==foo_bar"
        metrics:
          -  name: analytics/events
```

### ConstSource

Source name: `common/const`

> Returns a constant value (can be used to tweak a score of a feature).

#### `metrics` config

```yaml
    metrics:
      -  name: common/const
         weight: 100
```

### JiraSource

Source name: `common/jira`

> Returns a number of Jira ticket matching given JQL query.

#### `sources` config

```yaml
sources:
  - name: foo/jira
    kind: common/jira
    server: "https://foo-company.attlasian.net"
    user: "${JIRA_USER}"  # variables substitution
    password: "${JIRA_PASSWORD}" # Jira API key
```

Password is an API token that you can generate:
https://confluence.atlassian.com/cloud/api-tokens-938839638.html.

#### `metrics` config

```yaml
    metrics:
      # Jira
      - name: jira/p3-tickets
        source: foo/jira  # defined above
        query: "project = '{project}' AND Priority = 'P3' AND status = 'Open'"
        label: "%d P3 tickets"
```

#### `features` config

```yaml
    features:
      - name: FooBar
        template:
          - project: "Foo"  # this will be used in template string
        metrics:
          -  name: jira/p3-tickets
```

### LogstashSource

Source name: `common/logstash`

> Returns a number of entries matching a given elasticsearch query.

We assume that elasticsearch indices follow logstash naming convention
and are sharded by date, e.g. `logstash-access-log-2017.05.09`

#### `sources` config

```yaml
sources:
  - name: foo/logstash
    kind: common/logstash
    host: ${ELASTIC_HOST}
    index: logstash-access-log  # will query this index (e.g. logstash-access-log)
    period: 3600  # in seconds, query entries from the last hour (defaults to 86400 s)
```

#### `metrics` config

```yaml
    metrics:
      - name: logstash/get-requests-access-log
        source: foo/logstash  # defined above
        query: "request: 'GET' AND url: '{url}'"
        label: "%d GET request"
```

#### `features` config

```yaml
    features:
      - name: FooBar
        template:
          - url: "/foo"  # this will be used in template string
        metrics:
          -  name: logstash/get-requests-access-log
```

### MysqlSource

Source name: `common/mysql`

> Returns a number result for a given SQL query.

#### `sources` config

```yaml
sources:
  - name: foo/mysql
    kind: common/mysql
    host: "${DATABASE_HOST}"
    database: "app_database_name"
    user: "${DATABASE_USER}"
    password: "${DATABASE_PASSWORD}"
```

#### `metrics` config

```yaml
    metrics:
      # Get some stats
      - name: users/count
        source: foo/mysql
        query: "SELECT count(*) FROM users WHERE user_group = %(user_group)s"
        label: "{user_group} group members: %d"
```

Please note that only the first column from the first row in the results set will be taken.

#### `features` config

```yaml
    features:
      - name: FooBar
        template:
          - user_group: "Admin"  # this will be used in query defined above
        metrics:
          -  name: users/count
```

## Sources setup

Each source used should be set up / configured in YAML config file:

```yaml
sources:
  - name: wikia/jira
    kind: common/jira
    host: "the-company.attlasian-inc.com"
    user: "${JIRA_USER}"  # variables substitution
    password: "${JIRA_PASSWORD}" # Jira API key
```

`kind` key defines the name of Mike's source that will be set up using specified settings (e.g. JIRA credentials).
`name` is the name under which it will be available for feature's metrics.

Values defined in `sources` section are passed to the constructor of a source class that extends `SourceBase`.

```yaml
metrics:
  # Jira
  - name: jira/p3-tickets
    source: wikia/jira  # see above
    query: "project = '{project}' AND Priority = 'P3' AND status = 'Open'"  # you can use template strings
    label: "%d P3 tickets"
```

Sources are used via `metrics` that provide a specific value (e.g. number of tickets matching a given JQL query).
`source` specifies which source configured above to use.

Values defined in `metrics` section are passed to the `get_value` method of source class that extends `SourceBase`.

```yaml
  - metrics:
    -  name: jira/p3-tickets
```

Finally, we specify the list of metrics for each feature.

Each feature can provide a list of template variables that will be used to replace `{varname}` placeholder defined in `query` parameters for metrics.

```yaml
features:
  - name: DynamicPageList
    url: http://docs.company.net/pages/DynamicPageList
    template:
      - project: "DynamicPageList"  # this will be used in template string
      - tag: "dpl"
```

We can also put common ones in `common` section (for instance Jira statistics should probably be gathered for all features):

```yaml
common:
  # these keys will be copied to each feature defined below
  - metrics:
    -  name: jira/p2-tickets
    -  name: jira/p3-tickets
```
