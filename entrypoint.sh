#!/bin/bash -xe
# Used as the docker container's start script.
# This script accepts an action as a single argument to determine which service to start

ARG1=${1-cli}
ARG2=${2-}

if [ $ARG1 = 'cli' ]
then
    /bin/bash
elif [ $ARG1 = 'tests' ]
then
    if [ $ARG2 = 'pytest-cov.txt' ]
    then
        /.venv/bin/python -m pytest --cache-clear --cov=ppaya_lambda_utils tests > pytest-cov.txt
    else
        /.venv/bin/python -m pytest $ARG2 -s --cache-clear --cov=ppaya_lambda_utils
    fi
elif [ $ARG1 = 'lint' ]
then
    /.venv/bin/flake8 ./ppaya_lambda_utils ./tests
    /.venv/bin/mypy --config-file mypy.ini ./ppaya_lambda_utils ./tests
elif [ $ARG1 = 'docs' ]
then
    source /.venv/bin/activate; cd docs && PYTHONPATH=../salesforce_service make html
fi
