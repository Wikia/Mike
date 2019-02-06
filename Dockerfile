FROM python:3.6-slim

# label the image with branch name and commit hash
LABEL maintainer="maciej.brencz@gmail.com"
ARG BRANCH="master"
ARG COMMIT=""
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}

WORKDIR /opt/mike

# install dependencies
ADD setup.py .
ADD mycroft_holmes/__init__.py mycroft_holmes/
ADD mycroft_holmes/bin mycroft_holmes/bin

RUN apt-get update && apt-get install -y libmariadbclient-dev gcc \
    && pip install -e . \
    && rm -rf ~/.cache/pip \
    && apt-get remove -y gcc && apt-get autoremove -y

# copy the rest of the files
ADD . .

# expose the HTTP port
EXPOSE 5000

# your custom config YAML should be mounted
# and MIKE_CONFIG env variable should point to it
ENV MIKE_CONFIG /opt/mike/example.yaml

ENV COMMIT_SHA=${COMMIT}
ENV COMMIT_BRANCH=${BRANCH}

# entrypoint script
RUN echo "gunicorn 'mycroft_holmes.app.app:setup_app()' --worker-class sync -b 0.0.0.0:5000 --workers 4 --access-logfile -" > entrypoint

# run the app
CMD ["sh", "entrypoint"]
