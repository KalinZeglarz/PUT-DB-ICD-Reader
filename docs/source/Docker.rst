How to Use with Docker
======================

Prerequisites
""""""""""""""""""""""""
* Docker (Docker desktop, toolbox, etc.)
* Kitematic (optional, GUI for Docker)
* Source code with Dockerfile
* Configured database

Creating Container Image
""""""""""""""""""""""""
To create docker container open console in directory with Dockerfile.
Run command (you can replace tag value):

.. code-block:: bash

    docker build --tag icd_mapper .

.. important:: Check requirements.txt

   Before creating container remove unneeded modules from requirements.txt
   (like Sphinx modules).

Running Container
"""""""""""""""""
To create container use docker run:

.. code-block:: bash

    docker run --name CONTAINER_NAME -p EXTERNAL_PORT:DOCKER_PORT IMAGE_NAME

.. rubric:: Configuration

Container must be configurated with environmental variables
to function properly.

* icd_api_credentials_client_id - client id for ICD-11 API
  authentication (Defualt: none)
* icd_api_credentials_client_secret - client secret for ICD-11 API
  authentication (Default: none)
* db_parameters_database - database type (default: mysql+mysqlconnector)
* db_parameters_host - database host address (default: localhost:3306)
* db_parameters_user - database user (default: root)
* db_parameters_password - database password (default: root)
* server_host - address on which HTTP server will be run (default: 0.0.0.0)
* server_port - port on which HTTP server will be run (default: 5000)
