# ksweb

[![Build Status](https://travis-ci.org/puria/ksweb.svg?branch=master)](https://travis-ci.org/puria/ksweb)
[![Coverage Status](https://coveralls.io/repos/github/puria/ksweb/badge.svg?branch=master)](https://coveralls.io/github/puria/ksweb?branch=master)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fpuria%2Fksweb.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fpuria%2Fksweb?ref=badge_shield)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

The **KS** (Knowledge Shaper) is a [Document Automation](https://en.wikipedia.org/wiki/Document_automation) digital product that enables the shaping and reuse of Knowledge Bases. Our effort is to allow and facilitate the creation of wizards that easily outputs documents just by answering to simple questions with an extra effort to a functiona design and UX.

You can try the demo online available on [ks.studiolegale.it](http://ks.studiolegale.it).
Some example of Knowledge Bases are:
 
 * [Memorandum on GDPR compliance](https://github.com/marco55555/Memorandum-GDPR)
 * [Lawyer quotation (in italian)](https://github.com/marco55555/preventivo_avvocato)

<details>
 <summary><strong>:triangular_flag_on_post: Table of Contents</strong> (click to expand)</summary>

* [Getting started](#whale-getting-started)
* [Manual Installation](#floppy_disk-manual-installation-for-advanced-users)
* [Usage](#video_game-usage)
* [Configuration](#wrench-configuration)
* [I18n](#globe_with_meridians-I18n)
* [Notes](#memo-notes)
* [Troubleshooting & debugging](#bug-troubleshooting--debugging)
* [Acknowledgements](#heart_eyes-acknowledgements)
* [Contributing](#busts_in_silhouette-contributing)
* [License](#briefcase-license)
</details>

## :whale: Getting started

The easiest way to run ksweb is inside a docker container. just run

    git clone --recursive https://github.com/puria/ksweb.git
	cd ksweb
    docker-compose up

For instructions about how to install `docker-compose` please refere to the 
[official documentation](https://docs.docker.com/compose/install/) 

## :floppy_disk: Manual Installation (for advanced users)

Checkout the project

    git clone --recursive https://github.com/puria/ksweb.git

### Pre-requisites
Before install KSweb you need to have an instance of **[:leaves:mongodb](https://www.mongodb.com/download-center/community)** up and running, the **python development headers** and **python3-virtualenv** packages
*NB* you need `python3 >= 3.6` and `pip >= 18.1`

You also need to have to install [pandoc](https://pandoc.org/) for exporting the actual output to different formats.

### Installer
run the installer:

:apple: macosx

    brew install python3
    cd ksweb
    ./install

:penguin: debian derivatives

    apt install python3-dev python3-virtualenv
    cd ksweb
    ./install

### Manual installation

[![asciicast](https://asciinema.org/a/yImfeZTmmoGWvXV93k3g0OtaO.png)](https://asciinema.org/a/yImfeZTmmoGWvXV93k3g0OtaO)


Install ``ksweb`` using the setup.py script

```bash
    # Enter into the first project folder
    $ cd ksweb
    
    # Create a virtual environment for python2 (important)
    $ virtualenv -p python2 venv
    
    # Activate your virtual environment (very important)
    $ source venv/bin/activate
    
    # Enter the subproject folder
    $ cd ksweb
    
    # Install all the dependencies
    $ pip install -e .
    
    # Populate the mandatory data (TO RUN JUST AT THE FIRST USAGE OF A DATABASE)
    $ gearbox setup-app
```

Start the http server

```bash
 # Start a local webserver (NOT SUITABLE FOR PRODUCTION) 
 $ gearbox serve --reload
```

Then you are ready to go :tada:

***
## :video_game: Usage

To run the webapp activate your virtualenv and run the server:

    cd ksweb
    source venv/bin/activate
    gearbox serve

and head your browser to `http://localhost:8080`


Default accounts (username - password):

  Administrator: admin :key: adminks
  
  Lawyer: lawyer :key: lawyerks
  
  User: user :key: userks

***
## :wrench: Configuration

The conf files are `development.ini` and `test.ini`.

The most effective way is to edit the file and tweak stuff. Salient info are reported below.

### :leaves: MongoDB 

The url of the database connection is `ming.url` find it in `development.ini` and change it per your needs.

***

## :globe_with_meridians: I18n

The UI of the knowledge shaper is already translated in English and Italian.
If you need othe languages, please indicate us someone who wants to help, and
open and issue.
The extensive documentation about how the translation works is available on 
[this section](https://turbogears.readthedocs.io/en/latest/turbogears/i18n.html)
of the Turbogears official site.

In briefe allows to:

  * Create a new language (also called `Catalog`)
  * Extract the strings from the software
  * Update and Compile existing language/catalog

The catalogs are simple `.po` files that anyone can open with a translation
software (eg. [Poedit](https://poedit.net/))


***
## :memo: Notes

***
## :bug: Troubleshooting & debugging

To run the app in debug mode launch the server with the following flags

    gearbox serve --debug --reload


***
## :heart_eyes: Acknowledgements

Copyright (C) 2018 by StudioLegale.it <http://studiolegale.it>

Designed, written by AXANT.it and currently maintained by Puria Nafisi Azizi.

***
## :busts_in_silhouette: Contributing

1. [FORK IT](https://github.com/puria/ksweb/fork)
1. Create your feature branch `git checkout -b feature/branch`
1. Commit your changes `git commit -am 'Add some fooBar'`
1. Push to the branch `git push origin feature/branch`
1. Create a new Pull Request
1. Thank you

***
## :briefcase: License

    Knowledge Shaper, Collaborative knowledge tools editor
    Copyright (c) 2017-TODAY StudioLegale.it <http://studiolegale.it>
                             AXANT.it <http://axant.it>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fpuria%2Fksweb.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fpuria%2Fksweb?ref=badge_large)

