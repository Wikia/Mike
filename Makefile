coverage_options = --include='mycroft_holmes/*' --omit='test/*'

init:
	pip install -e .[dev]

test:
	pytest -v

lint:
	pylint mycroft_holmes

coverage:
	rm -f .coverage*
	rm -rf htmlcov/*
	coverage run -p -m pytest -v
	coverage combine
	coverage html -d htmlcov $(coverage_options)
	coverage xml -i
	coverage report $(coverage_options)

# UI
server_dev:
	FLASK_ENV=development gunicorn 'mycroft_holmes.app.app:setup_app()' --log-level DEBUG --worker-class sync --reload -b 0.0.0.0:5000 --workers 1 --access-logfile -

server:
	gunicorn 'mycroft_holmes.app.app:setup_app()' --worker-class sync -b 0.0.0.0:5000 --workers 4 --access-logfile -

# test database
mysql_cli:
	mysql -h127.0.0.1 -u${TEST_DATABASE_USER} -p${TEST_DATABASE_PASSWORD} ${TEST_DATABASE}

.PHONY: test
