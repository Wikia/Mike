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

## Config file

[An example YAML config file](https://github.com/Wikia/Mike/blob/master/test/fixtures/config.yaml) can be found in `test/fixtures` directory.

[Mike's architecture, sources structure and configuration](https://github.com/Wikia/Mike/tree/master/mycroft_holmes/sources#sources) are described in `mycroft_holmes/sources` directory.

## License

[Dashboard sidebar's background image](https://commons.wikimedia.org/wiki/File:Gree-02.jpg) is used under public domain license. Favicon made by [Freepik](https://www.flaticon.com/authors/freepik) is licensed by CC 3.0 BY.
