default: test

test: env
	.env/bin/py.test -x tests --cov=pact --cov-report=html

env: .env/.up-to-date


.env/.up-to-date: setup.py Makefile test_requirements.txt doc/pip_requirements.txt
	virtualenv --no-site-packages .env
	.env/bin/pip install -e .
	.env/bin/pip install -r ./*.egg-info/requires.txt || true
	.env/bin/pip install -r test_requirements.txt -r doc/pip_requirements.txt
	touch $@

doc: env
	.env/bin/python setup.py build_sphinx -a -E

