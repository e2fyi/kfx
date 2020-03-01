force_reload:

dev:
	pipenv install --dev
	pipenv run pip install -e .

dists: requirements sdist bdist wheels

docs: force_reload
	pipenv run sphinx-build rst docs -b dirhtml -E -P

requirements:
	pipenv run pipenv_to_requirements

sdist: requirements
	pipenv run python setup.py sdist

bdist: requirements
	pipenv run python setup.py bdist

wheels: requirements
	pipenv run python setup.py bdist_wheel

publish: dists
	pipenv run twine upload --verbose --disable-progress-bar dist/*

format:
	# docformatter --in-place kfx/**/*.py
	pipenv run isort kfx -rc
	pipenv run black kfx

check:
	pipenv run isort kfx -rc -c
	pipenv run black --check kfx
	pipenv run pylint kfx
	pipenv run flake8
	pipenv run mypy kfx
	pipenv run pydocstyle
	pipenv run bandit -r kfx -x *_test.py

test: check
	pipenv run pytest --cov=kfx

test-all: test dists
	pipenv run twine check dist/*

test-only: env
	pipenv run pytest --cov=kfx

test-ci: test-all
	pipenv run coveralls

schema: force_reload
	PYTHONPATH=${PWD} ./scripts/generate_schemas.py

commit: docs requirements force_reload
	git add .
	git commit