Sources
=======

This directory contains implementation of various source that provide values for metrics.

## Available sources

* `common/analytics` (gets data from Google Analytics)
* `common/elastic` (gets number of entries matching a given query against specified ElasticSearch index)
* `common/jira` (counts of tickets)
* `common/mysql` (performs a specified SQL query that returns a single value)

And a special source:

* `common/const` (returns a specified value, can be used to tweak a score of a feature)

#### Wikia-specific sources

* `wikia/wikifactory` (queries WikiFactory database that is used to configure every wiki Wikia hosts)

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

Sources are used via `metrics` that provide as specific value (e.g. number of tickets matching a given JQL query).
`source` specifies which source configured above to use.

```yaml
  - metrics:
    -  name: jira/p2-tickets
```

Finally, we specify the list of metrics for each feature.
