
py_sources = common/ daemons/ domain/ gateways/ handlers/ usecases/ utils/
pytest_flags = -p no:warnings --cov=. --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=90
mypy_flags = --warn-unused-configs --disallow-incomplete-defs --no-implicit-optional --warn-redundant-casts --warn-unused-ignores

default: help

.PHONY: help
help:
	@echo "Use 'make build' to generate the docker image and 'make run' to launch it."

.PHONY: clean
clean:
	find . -name __pycache__ -exec rm -rf {} \;
	find . -name \.pytest_cache -exec rm -rf {} \;
	find . -name \.mypy_cache -exec rm -rf {} \;
	find . -name \*\.py[cod] -exec rm -rf {} \;
	rm -rf htmlcov coverage
	rm .coverage coverage.xml

.PHONY: clean-all
clean-all: clean
	rm -rf .serverless node_modules .vscode .env

.PHONY: mypy
mypy:
	mypy $(mypy_flags) ${py_sources} tests/

.PHONY: black-check
black-check:
	black --check $(py_sources) tests/

.PHONY: black
black:
	black $(py_sources) tests/

.PHONY: isort-check
isort-check:
	isort --ac --check-only $(py_sources) tests/

.PHONY: check
check: isort-check black-check mypy

.PHONY: isort
isort:
	isort --ac $(py_sources) tests/

.PHONY: fmt
fmt: black isort

.PHONY: test
test:
	# We need those variables set before the tests run because some modules use them as indexes for dicts
	ENVIRONMENT=test \
	ES_INDEX=dev-token \
	ELASTIC_TX_INDEX=dev-tx \
	ELASTIC_TOKEN_BALANCES_INDEX=dev-token-balance \
	pytest $(pytest_flags) ./tests

stage=dev
# The "AWS_SDK_LOAD_CONFIG=1" is needed to load the AWS credentials from the ~/.aws/config file
# This is part of the solution to make it work with `aws sso login`
.PHONY: deploy-lambdas
deploy-lambdas:
	AWS_SDK_LOAD_CONFIG=1 npx serverless deploy --stage $(stage) --region eu-central-1

.PHONY: deploy-lambdas-ci
deploy-lambdas-ci:
	npx serverless deploy --stage $(stage) --region eu-central-1

.PHONY: install
install:
	npm install
	poetry install

.PHONY: build
build:
	docker-compose build

.ONESHELL:
.PHONY: deploy-daemons
deploy-daemons:
	if [ -z "${AWS_ACCOUNT_ID}" ]; then \
		echo "Please export a AWS_ACCOUNT_ID env var before running this"; \
		exit 1; \
	fi

	if [ -z "${DOCKER_IMAGE_TAG}" ]; then \
		commit=`git rev-parse HEAD`; \
		timestamp=`date +%s`; \
		export DOCKER_IMAGE_TAG="dev-$$commit-$$timestamp"; \
	fi \

	aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $$AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com; \
	docker build -t $$AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/hathor-explorer-service:$$DOCKER_IMAGE_TAG -f Dockerfile_Daemons .; \
	docker push $$AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/hathor-explorer-service:$$DOCKER_IMAGE_TAG

.PHONY: run
run:
	docker-compose up

.PHONY: validate_docs
validate_docs:
	npx swagger-cli validate text/api-docs.yml

.PHONY: bundle_docs
bundle_docs:
	npx swagger-cli bundle -o openapi.yml -t yaml text/api-docs.yml
