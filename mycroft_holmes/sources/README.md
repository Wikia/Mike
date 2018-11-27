Sources
=======

This directory contains implementation of various sources that provide values for metrics.

## Available sources

* `common/const` Returns a constant value (can be used to tweak a score of a feature).
* `common/jira` Returns a number of Jira ticket matching given JQL query.

### TODO

* `common/analytics` (gets data from Google Analytics)
* `common/elastic` (gets number of entries matching a given query against specified ElasticSearch index)
* `common/mysql` (performs a specified SQL query that returns a single value)

#### Wikia-specific sources

* `wikia/wikifactory` (queries WikiFactory database that is used to configure every wiki Wikia hosts)

## `common/const`

Returns a constant value (can be used to tweak a score of a feature).

### `metrics` config

```yaml
    metrics:
      -  name: common/const
         weight: 100
```

## `common/jira`

Returns a number of Jira ticket matching given JQL query.

### `sources` config

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

### `metrics` config

```yaml
    metrics:
      # Jira
      - name: jira/p3-tickets
        source: foo/jira  # defined above
        query: "project = '{project}' AND Priority = 'P3' AND status = 'Open'"
        label: "%d P3 tickets"
```

### `features` config

```yaml
    features:
      - name: FooBar
        template:
          - project: "Foo"  # this will be used in template string
        metrics:
          -  name: jira/p3-tickets
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
