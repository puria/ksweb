[![Build Status](https://travis-ci.org/puria/ksweb.svg?branch=master)](https://travis-ci.org/puria/ksweb)
[![Coverage Status](https://coveralls.io/repos/github/puria/ksweb/badge.svg?branch=master)](https://coveralls.io/github/puria/ksweb?branch=master)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fpuria%2Fksweb.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fpuria%2Fksweb?ref=badge_shield)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)


1min installation
======================

GNU/Linux and macOS
---------

[![asciicast](https://asciinema.org/a/yImfeZTmmoGWvXV93k3g0OtaO.png)](https://asciinema.org/a/yImfeZTmmoGWvXV93k3g0OtaO)


Install ``ksweb`` using the setup.py script

    $ cd ksweb
    $ virtualenv -p python2 venv
    $ source venv/bin/activate
    $ pip install -e .
    $ gearbox setup-app

Start the http server

    $ gearbox serve --reload

Then you are ready to go :tada:


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


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fpuria%2Fksweb.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fpuria%2Fksweb?ref=badge_large)
