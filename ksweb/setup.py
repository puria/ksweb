# -*- coding: utf-8 -*-

#  Quickstarted Options:
#
#  sqlalchemy: False
#  auth:       ming
#  mako:       False
#
#

# This is just a work-around for a Python2.7 issue causing
# interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import sys
py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs = [
    'WebTest == 1.4.3',
    'nose',
    'coverage',
    'gearbox'
]

install_requires = [
    "TurboGears2 >= 2.3.8",
    "Beaker >= 1.8.0",
    "Genshi",
    "Kajiki >= 0.3.5",
    "ming>=0.4.3",
    "repoze.who",
    "tw2.forms",
    "tgext.admin >= 0.6.1",
    "WebHelpers2",
    "tgext.webassets==0.0.2",
    "libsass==0.8.3",
    "tgapp-registration==0.7.0",
    "tgext.mailer==0.0.2",
    "tgapp-resetpassword==0.1.3"

]

if py_version != (3, 2):
    # Babel not available on 3.2
    install_requires.append("Babel")

setup(
    name='ksweb',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    extras_require={
       'testing': testpkgs
    },
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'ksweb': [
        'i18n/*/LC_MESSAGES/*.mo',
        'templates/*/*',
        'public/*/*'
    ]},
    message_extractors={'ksweb': [
        ('**.py', 'python', None),
        ('templates/**.xhtml', 'kajiki', None),
        ('templates/**.html', 'genshi', None),
        ('public/**', 'ignore', None)
    ]},
    entry_points={
        'paste.app_factory': [
            'main = ksweb.config.middleware:make_app'
        ],
        'gearbox.plugins': [
            'turbogears-devtools = tg.devtools'
        ]
    },
    zip_safe=False
)
