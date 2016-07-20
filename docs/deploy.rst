
Deployment
----------

The standard use case is to run ``databench`` locally. However, Databench can also be deployed on servers/platforms that support deploying WebSocket applications.


Heroku
++++++

You need a ``Procfile`` file

.. code-block:: bash

	web: databench

and your ``requirements.txt`` file.
Databench will pick up the environment variable ``PORT``.
An example repository that is deployed on Heroku is `databench_examples_viewer`_.

.. _`databench_examples_viewer`: https://github.com/svenkreiss/databench_examples_viewer


Local Docker
++++++++++++

It is helpful to build and run the Docker image locally when developing:

.. code-block:: bash

    docker build --tag=databench .
    docker run --rm -p 0.0.0.0:5000:5000 -i -t databench


AWS Elastic Beanstalk
+++++++++++++++++++++

AWS Elastic Beanstalk builds a new Docker image from the Dockerfile. You can also run those images locally (see below), but this is not necessary for deploying to AWS.

Get the AWS Elastic Beanstalk command line client ``eb`` here: http://aws.amazon.com/code/6752709412171743
or ``brew install aws-elasticbeanstalk``. Its interface is oriented on git commands. So you can go to your project's directory (which is a git repository) initialize the project with ``eb init``. Answer a few questions. Once done, deploy the app with ``eb start``. That creates the environment. Once an environment is created, deploy with ``eb push``.

Example ``eb init`` options:

* Access Key ID: xxxxxxx
* Secret Access Key: xxxxxxx
* region: ``1) US East (Virginia)``
* application name: ``databench_examples``
* env name: ``databenchexamples_env``
* environment tier: ``1) WebServer::Standard::1.0``
* solution stack: ``41) 64bit Amazon Linux 2014.03 v1.0.1 running Docker 1.0.0``
* env type: ``2) SingleInstance``
* create RDS DB instance: no
* instance profile: pick one


Troubleshooting
===============

* ``no module named boto``: do ``pip install boto`` before ``eb start``.
* the web console is at ``https://console.aws.amazon.com/elasticbeanstalk/`` and make sure you are looking at the right region which can be selected in the top-right corner
* ``eb logs`` shows more details
* If deployments become even slower, check ``/var/log/docker-ps.log`` (part of the logs). It could be that some other docker image is still building in the background from a previous ``eb push``.
* ``eb start`` might timeout in your terminal. The Web interface usually shows "updating" a bit longer and it should finish within 10 minutes. The timeout does not affect the underlying build process.

