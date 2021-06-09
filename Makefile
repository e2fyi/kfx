.FORCE:

requirements:
	poetry export -f requirements.txt --output requirements.txt --extras all
	poetry export -f requirements.txt --output requirements-dev.txt --dev --extras all

build:
	poetry build

publish:
	poetry publish -u __token__ -p ${PYPI_TOKEN}

format:
	# docformatter --in-place kfx/**/*.py
	poetry run isort kfx
	poetry run black kfx

check:
	poetry run isort kfx -c
	poetry run black --check kfx
	poetry run pylint kfx
	poetry run flake8
	poetry run mypy kfx
	poetry run bandit -r kfx -x *_test.py

test: check
	poetry run pytest --cov=kfx

test-only: env
	poetry run pytest --cov=kfx

test-ci: test
	poetry run coveralls

schema: force_reload
	poetry run python ./scripts/generate_schemas.py

docs: .FORCE requirements
	poetry run mkdocs build

docs-serve: docs
	cd site/  && poetry run python -m http.server 8000