"""Deploy script for AxantWeb

Make sure you run this with something like -i ~/.ssh/repo
to use the repo key for authentication
"""

from __future__ import with_statement

APP_NAME = 'ksweb/ksweb'    # This is the directory where the app is cloned
APP_ID = '568'  # This is the USERID on the axantweb server
APP_REPOSITORY = 'http://repo.axant.it/hg/ksweb'    # This is repository from where to clone on first deploy
APP_DEPLOY_BRANCH = 'default'
APP_SUPPORTS_MIGRATIONS = False
APP_USES_GEVENT = False # Keep in mind that enabling GEVENT requires requires WSGIApplicationGroup %{GLOBAL} in Apache VHost conf

APP_NAME_AXANT = 'ksweb-axant/ksweb-axant'    # This is the directory where the app is cloned
APP_ID_AXANT = '572'  # This is the USERID on the axantweb server
APP_DEPLOY_BRANCH_AXANT = 'sprint2'
APP_USES_GEVENT_AXANT = False # Keep in mind that enabling GEVENT requires requires WSGIApplicationGroup %{GLOBAL} in Apache VHost conf


import time
import fabric
from fabric.api import *
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib.files import exists, append
import glob, os

APP_USER = 'aw%s' % APP_ID
APP_USER_AXANT = 'aw%s' % APP_ID_AXANT

env.hosts = ['%s@wsgi.axantweb.com' % APP_USER]
env.hosts_axant = ['%s@wsgi.axantweb.com' % APP_USER_AXANT]


APP_PATH = os.path.join('/var/www', APP_ID, 'app', APP_NAME)
ENV_PATH = os.path.join('/var/www', APP_ID, 'penv')

APP_PATH_AXANT = os.path.join('/var/www', APP_ID_AXANT, 'app', APP_NAME_AXANT)
ENV_PATH_AXANT = os.path.join('/var/www', APP_ID_AXANT, 'penv')


ENV_ACTIVATE = os.path.join(ENV_PATH, 'bin/activate')
ENV_ACTIVATE_AXANT = os.path.join(ENV_PATH_AXANT, 'bin/activate')

WSGI_APPLICATION = '''
from paste.deploy import loadapp

def init_application(path):
    APP_CONFIG = path + "/%s/staging.ini"
    application = loadapp("config:%%s" %% APP_CONFIG)
    return application
''' % APP_NAME

WSGI_APPLICATION_AXANT = '''
    from paste.deploy import loadapp
    
    def init_application(path):
    APP_CONFIG = path + "/%s/staging.ini"
    application = loadapp("config:%%s" %% APP_CONFIG)
    return application
    ''' % APP_NAME_AXANT



if APP_USES_GEVENT:
    WSGI_APPLICATION = '''import gevent
from gevent import monkey
monkey.patch_all()
''' + WSGI_APPLICATION

if APP_USES_GEVENT_AXANT:
    WSGI_APPLICATION_AXANT = '''import gevent
        from gevent import monkey
        monkey.patch_all()
        
        ''' + WSGI_APPLICATION_AXANT


def _wait(seconds):
    for i in range(seconds, 0, -1):
        if i <= 2:
            i = colors.red('%s' % i)
        elif i <= 4:
            i = colors.yellow('%s' % i)
        print 'Starting in %s...' % i
        time.sleep(1.0)


def _cmd_in_venv(cmd):
    return 'source %s; %s' % (ENV_ACTIVATE, cmd)

def _cmd_in_venv_AXANT(cmd):
    return 'source %s; %s' % (ENV_ACTIVATE_AXANT, cmd)


def _first_deploy():
    # This is required to make gearbox available, otherwise only TurboGears gets installed
    run(_cmd_in_venv('pip install "tg.devtools==2.3.8"'))

    with cd('app'):
        run('hg clone %s' % APP_REPOSITORY)
        run('rm wsgi_application.py')
        append('wsgi_application.py', WSGI_APPLICATION)
        

def _first_deploy_AXANT():
    # This is required to make gearbox available, otherwise only TurboGears gets installed
    run(_cmd_in_venv_AXANT('pip install "tg.devtools==2.3.8"'))
    
    with cd('app'):
        run('hg clone %s' % APP_REPOSITORY)
        run('rm wsgi_application.py')
        append('wsgi_application.py', WSGI_APPLICATION_AXANT)



def deploy_dev():
    is_first_deploy = not exists(APP_PATH)
    if is_first_deploy:
        print 'Performing First deploy!'
        _first_deploy()

    with cd(APP_PATH):
        run('hg pull -u')
        run('hg update -C %s' % APP_DEPLOY_BRANCH)
        run(_cmd_in_venv('python setup.py develop'))

        if is_first_deploy:
            run(_cmd_in_venv('gearbox setup-app -c staging.ini'))
        else:
            if APP_SUPPORTS_MIGRATIONS:
                run(_cmd_in_venv('gearbox migrate -c staging.ini upgrade'))

    if not APP_USES_GEVENT:
        run('touch run.wsgi')
    else:
        # GEVENT doesn't work with a plain touch, needs apache restart
        run('touch /tmp/please_restart_apache_in_5_minutes')
        print colors.yellow('USING GEVENT THE SERVER WILL TAKE UP TO 5 MINUTES TO RESTART')
        _wait(60*5)


def deploy_axant():
    is_first_deploy = not exists(APP_PATH_AXANT)
    if is_first_deploy:
        print 'Performing First deploy!'
        _first_deploy_AXANT()

    with cd(APP_PATH_AXANT):
        run('hg pull -u')
        run('hg update -C %s' % APP_DEPLOY_BRANCH_AXANT)
        run(_cmd_in_venv_AXANT('python setup.py develop'))
        
        if is_first_deploy:
            run(_cmd_in_venv_AXANT('gearbox setup-app -c staging-axant.ini'))
        else:
            if APP_SUPPORTS_MIGRATIONS:
                run(_cmd_in_venv_AXANT('gearbox migrate -c staging-axant.ini upgrade'))

    if not APP_USES_GEVENT_AXANT:
        run('touch run.wsgi')
    else:
        # GEVENT doesn't work with a plain touch, needs apache restart
        run('touch /tmp/please_restart_apache_in_5_minutes')
        print colors.yellow('USING GEVENT THE SERVER WILL TAKE UP TO 5 MINUTES TO RESTART')
        _wait(60*5)



def check_dev_log():
    run(' tail -f -n 100 /var/log/circus/ksweb.test.axantweb.com.log ')