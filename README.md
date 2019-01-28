# Mike [![Build Status](https://travis-ci.org/Wikia/Mike.svg?branch=master)](https://travis-ci.org/Wikia/Mike)

![](https://github.com/Wikia/Mike/raw/master/docs/Mike_dashboard.png)

### [Mycroft Holmes](https://en.wikipedia.org/wiki/The_Moon_Is_a_Harsh_Mistress#Characters) (High-Optional, Logical, Multi-Evaluating Supervisor) aka Mike.

[The tool that collects metrics for software components](https://medium.com/legacy-systems-diary/our-story-about-sustaining-engineering-team-7e83652b8873) based on: bug reports / tickets, features usage and the code quality.

## Install

```
virtualenv -ppython3 env
. env/bin/activate
pip install -e .
```


To install development dependencies run `make` inside virtualenv.

## Set up a config file

Please refer to `test/fixtures/config.yaml` and README.md in `mycroft_holmes/source` directory and prepare your own config file.

Save it and store its path in `MIKE_CONFIG` env variable. It is used by the front-end app and metrics collector script.

Otherwise you'll get:

```
AssertionError: Please specify where your config YAML file is in MIKE_CONFIG env variable.
```

## Running UI

`Mycroft Holmes` comes with Flask-powered web-application that provides a dashboard with an overview of components and their metrics.

Run the following to try it out in development mode:

```
make server_dev
```

Now visit [`/version.json`](http://127.0.0.1:5000/version.json).

### Collecting metrics

Let's assume that this repository has been cloned into ` /home/macbre/github/Mike` and virtual env has been set up.
Now add the following to your `crontab`:

```
SHELL=/bin/bash
# m h  dom mon dow   command
2 2,14 *   *   *     ( cd /home/macbre/github/Mike && source env/bin/activate && source .env && collect_metrics test/fixtures/config.yaml ) >> /home/macbre/Mike.log 2>&1
```

## Using Docker

You can use our [official Docker image](https://hub.docker.com/r/macbre/mike):

```
docker pull macbre/mike:latest
docker run -p5000:5000 -it mike
```

Run the following command periodically to keep metrics up to date:

```
docker run -it mike collect_metrics
```

### Passing your custom YAML config file

By default Mike docker container will use a sample config file located in `/example.yaml`. You should use your own.
Please refer to "Set up a config file" section above.

Assuming that you have a local `/home/mike/config/.env` file with all your specific credentials that are referenced in `/home/mike/config/mike.yaml`
config. Run the following:

```
docker run -v /home/mike/config:/opt/config -p5000:5000 --env-file /home/mike/config/.env -e MIKE_CONFIG=/opt/config/mike.yaml -it mike
```

`.env` file should look like the following:

```
DATABASE_USER=mike_db
DATABASE_PASSWORD=d97b4e7998a07bd1b2da4c21f29ec183ad3eec20
```

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

> `TEST_DATABASE` env variable needs to be set to run these tests. `schema.sql` and `schema_test.sql` files need to be applied as well. Please refer to `.travis.yml` when in doubt.

You may want to include storage integration tests. They do require running MySQL server. Connection details are provided via env variables:

```
export TEST_DATABASE='mycroft_holmes'
export TEST_DATABASE_USER='foo'
export TEST_DATABASE_PASSWORD='bar'

make test

# access mysql console with the above credentials
make mysql_cli
```
