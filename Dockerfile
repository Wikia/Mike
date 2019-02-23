FROM python:3.6-alpine3.9

# label the image with branch name and commit hash
LABEL maintainer="maciej.brencz@gmail.com"
ARG BRANCH="master"
ARG COMMIT=""
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}

WORKDIR /opt/mike

# install dependencies
COPY setup.py .
COPY mycroft_holmes/__init__.py mycroft_holmes/
COPY mycroft_holmes/bin mycroft_holmes/bin

# @see https://leemendelowitz.github.io/blog/how-does-python-find-packages.html
# Python by default reads site packages from /usr/local/lib/python3.6/site-packages
# while apk install py3-lxml to /usr/lib/python3.6/site-packages
ENV PYTHONPATH /usr/local/lib/python3.6/site-packages:/usr/lib/python3.6/site-packages

RUN apk add --update --no-cache mariadb-connector-c py3-lxml \
    && apk add --no-cache --virtual .build-deps build-base mariadb-dev libffi-dev yaml-dev \
    && pip install -e . \
    && apk del .build-deps \
    && pip list

# copy the rest of the files
COPY . .

# expose the HTTP port
EXPOSE 5000

# your custom config YAML should be mounted
# and MIKE_CONFIG env variable should point to it
ENV MIKE_CONFIG /opt/mike/example.yaml

ENV COMMIT_SHA=${COMMIT}
ENV COMMIT_BRANCH=${BRANCH}

# entrypoint script
RUN echo "gunicorn 'mycroft_holmes.app.app:setup_app()' --worker-class sync -b 0.0.0.0:5000 --workers 4 --access-logfile -" > entrypoint

# do not run as root
RUN addgroup -g 9999 mycroft && \
    adduser -D -u 9999 -G mycroft mycroft
USER mycroft

# run the app
CMD ["sh", "entrypoint"]
