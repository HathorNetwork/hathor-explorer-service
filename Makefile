
py_sources = common/ daemons/ domain/ gateways/ handlers/ tests/ usecases/ utils/
pytest_flags = -p no:warnings --cov=. --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=90
mypy_flags = --warn-unused-configs --disallow-incomplete-defs --no-implicit-optional --warn-redundant-casts --warn-unused-ignores

default: help

.PHONY: help
help:
	@echo "Use 'make build' to generate the docker image and 'make run' to launch it."

.PHONY: mypy
mypy:
	mypy $(mypy_flags) ${py_sources}

.PHONY: flake8
flake8:
	flake8 $(py_sources)

.PHONY: isort-check
isort-check:
	isort --ac --check-only $(py_sources)

.PHONY: check
check: flake8 isort-check mypy

.PHONY: yapf
yapf:
	yapf -rip $(py_sources)

.PHONY: isort
isort:
	isort --ac $(py_sources)

.PHONY: fmt
fmt: yapf isort

.PHONY: test
test:
	ENVIRONMENT=test pytest $(pytest_flags) ./tests

.PHONY: deploy-lambdas-dev
deploy-lambdas-dev:
	serverless deploy --stage dev --region eu-central-1

.PHONY: deploy-lambdas-mainnet
deploy-lambdas-mainnet:
	serverless deploy --stage mainnet --region eu-central-1

.PHONY: build
build:
	npm install
	poetry install
	docker-compose build

.PHONY: build-daemons
build-daemons:
	if [[ -z "${AWS_ACCOUNT_ID}" ]]; then \
		echo "Please export a AWS_ACCOUNT_ID env var before running this"; \
		exit 1; \
	fi

	commit=`git rev-parse HEAD`; \
	aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $$AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com; \
	docker build -t $$AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/hathor-explorer-service:$$commit .; \
	docker push $$AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/hathor-explorer-service:$$commit

.PHONY: run
run:
	docker-compose -d up
	serverless offline --printOutput
