# -*- coding: utf-8 -*-

import sys

py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup, find_packages

testpkgs = ["WebTest ==2.0.30", "nose", "coverage", "gearbox", "backlash", "pre-commit"]

install_requires = [
    "TurboGears2==2.4.1",
    "Beaker==1.10.0",
    "PyYAML==5.1.1",
    "pypandoc==1.4",
    "Kajiki==0.8.0",
    "Ming==0.6.5",
    "repoze.who==2.3",
    "tw2.forms==2.2.5",
    "tgext.admin==0.7.4",
    "WebHelpers2==2.0",
    "tgext.webassets==0.0.2",
    "libsass==0.19.2",
    "tgapp-registration @ git+https://github.com/axant/tgapp-registration",
    "tgext.pluggable @ git+https://github.com/TurboGears/tgext.pluggable",
    "tgext.mailer @ git+https://github.com/amol-/tgext.mailer",
    "tgapp-resetpassword @ git+https://github.com/puria/tgapp-resetpassword",
    "tgext.datahelpers",
    "tgapp-userprofile @ git+https://github.com/puria/tgapp-userprofile",
    "axf==0.0.19",
    "tgext.evolve==0.0.4",
    "dukpy",
]

if py_version != (3, 2):
    # Babel not available on 3.2
    install_requires.append("Babel")

setup(
    name="ksweb",
    version="1.0",
    description="",
    author="",
    author_email="",
    url="",
    packages=find_packages(exclude=["ez_setup"]),
    install_requires=install_requires,
    extras_require={"testing": testpkgs},
    include_package_data=True,
    test_suite="nose.collector",
    tests_require=testpkgs,
    package_data={"ksweb": ["i18n/*/LC_MESSAGES/*.mo", "templates/*/*", "public/*/*"]},
    message_extractors={
        "ksweb": [
            ("**.py", "python", None),
            ("templates/**.xhtml", "kajiki", {"extract_python": True}),
            ("public/**", "ignore", None),
        ]
    },
    entry_points={
        "paste.app_factory": ["main = ksweb.config.middleware:make_app"],
        "gearbox.plugins": ["turbogears-devtools = tg.devtools"],
    },
    zip_safe=False,
)
