# About

Dokomo Forms is a self-hosted data collection and analysis platform, and is the successor to [Formhub](https://formhub.org/).

[![Build Status](https://travis-ci.org/SEL-Columbia/dokomoforms.svg?branch=master)](https://travis-ci.org/SEL-Columbia/dokomoforms)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/SEL-Columbia/dokomoforms?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Coverage Status](https://coveralls.io/repos/SEL-Columbia/dokomoforms/badge.svg?branch=master)](https://coveralls.io/r/SEL-Columbia/dokomoforms?branch=master)

[![Sauce Test Status](https://saucelabs.com/browser-matrix/dokomo_sauce_matrix.svg)](https://saucelabs.com/u/dokomo_sauce_matrix)

[![Dependency Status](https://gemnasium.com/SEL-Columbia/dokomoforms.svg)](https://gemnasium.com/SEL-Columbia/dokomoforms)

[![Documentation Status](https://readthedocs.org/projects/dokomoforms/badge/?version=latest)](https://readthedocs.org/projects/dokomoforms/?badge=latest)

# Phoenix

1. Organization owns instance, and all users belong to the organization. (TODO)

2. Filesystem-level encryption. (TODO)

3. i18n

4. Focus on questions rather than surveys. (TODO)

5. You can specify configuration options in `local_config.py` or as command line flags to [webapp.py](webapp.py). The available options are defined in [dokomoforms/options.py](dokomoforms/options.py)

6. [webapp.py](webapp.py) now sets up the tables for you (no more `manage_db.py`). If you want `$ manage_db.py -d`, run

  `$ ./webapp.py --kill=True`

  You can also specify the schema you want like `$ ./webappy.py --schema=whatever`

7. New way to run tests (after `$ pip install tox`):

  `$ tox`

  Or, if you want the coverage report as well,

  `$ tox -e cover`

  The tests only touch the `doko_test` schema (which they create/destroy for you).
  
# Using Docker for Local Dev Environment and Deployment

[Docker](https://en.wikipedia.org/wiki/Docker_(software)) is a container management software that aims at component separation and deployment automation. Please refer to [the Docker API](https://docs.docker.com/) for a fuller introduction.

## Using Docker Manually (Docker knowledge required)

There is a [Dockerfile](Dockerfile) in the root directory to build the Docker image of the Dokomo Forms webapp component building on top a Python 3 image. To build the webapp image, run 

> $ docker build -t selcolumbia/dokomoforms .

However, Dokomo Forms as a service needs other components such as the database in order to work. We have referenced `mdillon/postgis` as the image, since we are using PostgreSQL with the PostGIS extension. You may also substitute `mdillon/postgis` with any image includes PostGIS. A manual way to run Dokomo Forms as a service would involve starting the `postgis` container and linking it to the Dokomo Forms image we have just built, such as:

> $ docker run -d -p 8888:8888 --link postgis:db selcolumbia/dokomoforms

## Using Docker for Local Development

`docker-compose` is the program that automates Docker container building, running, and linking as described above. It uses the [docker-compose.yml](docker-compose.yml) file which is provided in the root directory.

To start the service locally, run:

> $ docker-compose up

Docker will download the necessary images, then build and link them. This step takes 3-5 minutes for the first build. Once the command has finished, you can visit [http://localhost:8888](http://localhost:8888) and start using Dokomo Forms.

## Using Docker for Automated Deployment

`docker-machine` is the program that automates the deployment process. It can hook into many VPS providers such as [AWS](http://aws.amazon.com/), [Rackspace](http://www.rackspace.com/) and [DigitalOcean](https://www.digitalocean.com/). 

Here is an example using DigitalOcean:

1. Obtain a token from DigitalOcean. Click on "Generate New Token" from the API page as indicated below.

  ![doapi](http://i.imgur.com/0SrmqX7.jpg)

2. Create a droplet with the token you have just acquired

  > $ docker-machine create -d digitalocean --digitalocean-access-token YOUR_ACCESS_TOKEN dokomoforms

3. Make your local Docker environment aware of this new machine

  > $ eval $(docker-machine env dokomoforms)

4. Run `docker-compose` with the new environment

  > $ docker-compose up -d

Now you have an instance of Dokomo Forms running on your DigitalOcean droplet!
