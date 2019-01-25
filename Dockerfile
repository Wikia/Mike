FROM python:3.6-alpine

WORKDIR /opt/mike

# install dependencies
ADD setup.py .
ADD mycroft_holmes/__init__.py mycroft_holmes/
ADD mycroft_holmes/bin mycroft_holmes/bin

RUN apk add --update --no-cache mariadb-connector-c \
    && apk add --no-cache --virtual .build-deps build-base mariadb-dev libffi-dev yaml-dev \
    && pip install -e . \
    && apk del .build-deps

# copy the rest of the files
ADD . .

# expose the HTTP port
EXPOSE 5000

# run the app
ENV FLASK_APP=mycroft_holmes/app/app.py
CMD ["flask", "run", "--host=0.0.0.0"]
