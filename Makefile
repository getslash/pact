default: test

test: env
	.env/bin/pytest -x tests --cov=pact --cov-report=html

env: .env/.up-to-date


.env/.up-to-date: Makefile pyproject.toml
	python -m venv .env
	.env/bin/pip install -e .[testing,doc]
	touch $@

doc: env
	.env/bin/sphinx-build -a -W -E doc build/sphinx/html

