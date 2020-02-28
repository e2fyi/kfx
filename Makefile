force_reload:

dev:
	pipenv install --dev
	pipenv run pip install -e .

dists: requirements sdist bdist wheels

docs: force_reload
	sphinx-build rst docs -b dirhtml -E -P

requirements:
	pipenv run pipenv_to_requirements

sdist: requirements
	pipenv run python setup.py sdist

bdist: requirements
	pipenv run python setup.py bdist

wheels: requirements
	pipenv run python setup.py bdist_wheel

publish: dists
	twine upload --verbose --disable-progress-bar dist/*

format:
	docformatter --in-place kfp/**/*.py
	isort kfp -rc
	black kfp

check:
	isort kfp -rc -c
	black --check kfp
	pylint kfp
	flake8
	mypy kfp
	pydocstyle
	bandit -r kfp

test: check
	pytest --cov=kfp

test-all: test dists
	twine check dist/*

test-only: env
	pytest --cov=kfp
