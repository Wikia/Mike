# Mike [![Build Status](https://travis-ci.org/Wikia/Mike.svg?branch=master)](https://travis-ci.org/Wikia/Mike)

[Mycroft Holmes](https://en.wikipedia.org/wiki/The_Moon_Is_a_Harsh_Mistress#Characters) (High-Optional, Logical, Multi-Evaluating Supervisor) aka Mike.

[The tool that collects metrics for software components](https://medium.com/legacy-systems-diary/our-story-about-sustaining-engineering-team-7e83652b8873) based on: bug reports / tickets, features usage and the code quality.

## Install

```
virtualenv -ppython3 env
. env/bin/activate
pip install -e .
```


To install development dependencies run `make` inside virtualenv.

## Running

> TODO

## Scripts

The following command line scripts are available in Mike's virtual environment:

### `collect_metrics`

This script should be run periodically to collect metrics for features defined in YAML config file.

Simply run `collect_metrics <path to YAML config file>`

Environment variables passed to the script will be used to replace variables in the YAML config file.

For instance, running the following:

```
DATABASE_USER=foo DATABASE_PASSWORD=2505eb2474b2 collect_metrics test/fixtures/config.yaml
```

will replace `${...}` placeholders with appropriate values taken from environment variables provided above.

```yaml
sources:
  - name: wikia/tags-report
    kind: common/mysql
    host: db.prod
    user: "${DATABASE_USER}"
    password: "${DATABASE_PASSWORD}"
```

[List of all available sources with full documentation](https://github.com/Wikia/Mike/tree/master/mycroft_holmes/sources#sources).

### `generate_source_docs`

Prints out Markdown with sources documentation taken from the code, to be pasted into `mycroft_holmes/sources/README>md`
when a new source is added or an existing one is updated.

## Config file

[An example YAML config file](https://github.com/Wikia/Mike/blob/master/test/fixtures/config.yaml) can be found in `test/fixtures` directory.

[Mike's architecture, sources structure and configuration](https://github.com/Wikia/Mike/tree/master/mycroft_holmes/sources#sources) are described in `mycroft_holmes/sources` directory.

## License

[Dashboard sidebar's background image](https://commons.wikimedia.org/wiki/File:Gree-02.jpg) is used under public domain license. Favicon made by [Freepik](https://www.flaticon.com/authors/freepik) is licensed by CC 3.0 BY.

## Tests

After setting up virtual env, please install all dependencies (including dev ones) via `make init`. Then run:

```
make test
```

### MySQL storage integration tests

> `TEST_DATABASE` env variable needs to be set to run these tests.

You may want to include storage integration tests. They do require running MySQL server. Connection details are provided via env variables:

```
export TEST_DATABASE='mycroft_holmes'
export TEST_DATABASE_USER='foo'
export TEST_DATABASE_PASSWORD='bar'

make test
```
