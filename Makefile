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

.PHONY: test
