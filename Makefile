#!make

APP_NAME := ppaya_lambda_utils_python
ENV_NAME := dev
AWS_REGION := ${AWS_REGION}


init-dev-venv:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements_docker_dev.txt
	.venv/bin/pip install -U docker-compose


build-local-container:
	docker-compose build cli


run-tests:
	TEST_ARGS=${TEST_ARGS} docker-compose run tests


run-lint:
	docker-compose run lint


run-cli:
	docker-compose run cli


build-docs:
	docker-compose run docs


clean-permissions:
	sudo chown ${USER}:${USER} -R .
