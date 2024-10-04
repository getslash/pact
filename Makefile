default: test

test: env
	.venv/bin/pytest -x tests --cov=pact --cov-report=html

env:
	uv venv
	uv pip install -e ".[testing]"

doc: env
	.venv/bin/sphinx-build -a -W -E doc build/sphinx/html

