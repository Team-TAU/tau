# TAU Production Deployment

If you wish, you can deploy TAU as you would other production Django applications.  This document will cover how to deploy TAU in a production environment on production systems, either in the cloud or on physical hardware. 

## Overview
TAU, as a Django application, does not have any special requirements for deployments outside of what a Django Channels application would require.  This document will not exhaustively cover how to deploy a Django application, but will cover the specifics of TAU.

## Requirements
A production deployment of TAU requires the following:
* A domain name, with DNS pointed to your hosting environment
* Python 3.8+
* Node.js 16+
* daphne 
* supervisord
  * We recommend using this fork of supervisord, as the version of supervisord-stdout in PyPI is not Python 3 compatible: https://github.com/coderanger/supervisor-stdout
* A Django compatible database (PostgreSQL, MySQL, etc.)
  * TAU has been tested with PostgreSQL 13
* A Django-compatible cache (Redis, Memcached, etc.)
    * TAU has been tested with Redis 6

## Docker
While TAU does not have a Docker image in Docker Hub or another container image registry, the repository does contain a Dockerfile that can be used to build a Docker image.  This Docker image can be used to deploy TAU in a production environment.  The Dockerfile is located in the root of the repository, and can be built with the following command:

    docker build -t tau .

TAU is almost exclusively run in a Docker container in production, and the Dockerfile is the recommended way to deploy TAU in a production environment.

### Configuration

The Docker container uses environment variables to configure TAU. Two sample environment files, `.env_sample` and `.env_single_container_samle` are provided, based on whether you are deploying TAU and its dependencies on the same host, or if they are hosted externally. For a full list of environment variables, see [Environment Variables](../env_options.md).

### Docker Compose

The included Docker Compose file can be used to deploy TAU in either a development or production environment. This Compose file expects configuration to be stored within the file `.env`. See [Configuration](#configuration) for more information on how to set up the environment file.

Once your environment file is configured, you can deploy TAU with the following command:

    docker-compose up -d

### Docker Swarm

The included Docker Compose file is not yet suitable for deployment with Docker Swarm. A future update will update the Compose file to be compatible with Docker Swarm.

## Kubernetes

Deploying TAU in Kubernetes is not yet supported. A future update will add support for deploying TAU in Kubernetes, and will include a Helm chart.

## Manual Deployment
We don't currently have a guide for manually deploying TAU in a production environment, as all users currently running TAU are running it in some sort of OCI container runtime. However, the steps outlined in the Dockerfile can be used as a guide for building the Vue frontend components and setting up the environment for running TAU.  If you would like to contribute a guide for manual deployments, please open a pull request. 

## Proxying and SSL

Running TAU in a production environment requires SSL termination for both the OpenID authorization flow callbacks and for receiving Twitch EventSub callbacks. If you are deploying TAU to a large public cloud provider like AWS, GCP, or Azure, you can use their load balancers to handle SSL termination. If you are deploying TAU to a smaller cloud provider, or to a physical server, you will need to set up a reverse proxy to handle SSL termination. 

Several reverse proxes are available, such as Nginx, Caddy, or Traefik. The latter two can automatically obtain SSL certificates from Let's Encrypt, which for most users is an easy and optimal solution. Please refer to the documentation for your chosen reverse proxy for more information on how to set it up.

TAU will need to be configured to be aware that it is running behind a proxy. Specifically, you'll need to set the `PUBLIC_URL`, `PROTOCOL`, and `BEHIND_PROXY` environment variables. The `PUBLIC_URL` should be the domain name you are using for TAU, and the `PROTOCOL` should be `https:`. The `BEHIND_PROXY` environment variable should be set to `True`.

### Health Checks

You will likely want to set up health checks for your reverse proxy. The best healthcheck endpoint is available through the API. Please see the [heartbeats](../api/v1.md#heartbeats) portion of the API documentation for more information.