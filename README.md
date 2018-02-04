[![Build Status](https://travis-ci.org/puria/ksweb.svg?branch=master)](https://travis-ci.org/puria/ksweb)
[![Coverage Status](https://coveralls.io/repos/github/puria/ksweb/badge.svg?branch=master)](https://coveralls.io/github/puria/ksweb?branch=master)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)


This file is for you to describe the ksweb application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``ksweb`` using the setup.py script::

    $ cd ksweb
    $ python setup.py develop

Create the project database for any model classes defined::

    $ gearbox setup-app

Start the paste http server::

    $ gearbox serve

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ gearbox serve --reload --debug

Then you are ready to go.


Example Account
===============

There are 3 level of permission:

- Administrator: For site admin.
- Lawyer: For the lawyer.
- User: User that responde at the questionary.


Default account (username - password)::

    Administrator: admin - adminks
    Lawyer: lawyer - lawyerks
    User: user - userks
