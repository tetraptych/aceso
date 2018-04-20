lint:
	flake8 aceso

test:
	pytest -s tests

coverage:
	pytest --cov=aceso --cov-config .coveragerc --cov-fail-under=0 --cov-report term-missing
