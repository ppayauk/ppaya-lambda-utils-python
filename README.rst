=========================
PPAYA Lambda Utils Python
=========================

A library of utilities commonly used internally at PPAYA within our
python SAM_ (Serverless Application Model) services.

The utilities are mostly used to reduce the boilerplate involved in our
standard usage of boto3_ and aws_lambda_powertools_.

This is still very much a work in progress and features are driven by internal
requirments.

Setting up a local dev environment
==================================

You will need Docker_ installed on your local machine. The image used is the
same as the AWS SAM CLI uses to build artefacts.

*docker_dev.env* provides the environmental variables to be used at run-time
within your local docker container for tests and debugging. You shouldn't
commit any sensitive information or credentials to this file.

Rebuilding environment
======================

If you add any requirements to the library or the development environment
(ie requirments_docker_dev.txt) you will need to rebuild the docker container::

    make build-local-container

Testing
=======

To run the test suite in a docker container::

    make run-tests

Linting
=======

To run flake8 and mypy type checking in a docker container::

    make run-lint

Documentation
=============

To build the documentation::

    make build-docs



.. _Docker: https://hub.docker.com/search/?type=edition&offering=community
.. _aws_lambda_power_tools: https://awslabs.github.io/aws-lambda-powertools-python/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _SAM: https://aws.amazon.com/serverless/sam/
.. _aws_lambda_powertools: https://awslabs.github.io/aws-lambda-powertools-python/
.. _boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
