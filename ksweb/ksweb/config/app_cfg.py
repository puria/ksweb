# -*- coding: utf-8 -*-
from tg.configuration import AppConfig
from tg.configuration.auth import TGAuthMetadata
from tg import milestones

import ksweb
from .evolutions import evolutions
from ksweb import model, lib

base_config = AppConfig()
base_config.renderers = []
base_config.disable_request_extensions = False
base_config.dispatch_path_translator = True
base_config.prefer_toscawidgets2 = True
base_config.package = ksweb
base_config.renderers.append('json')
#base_config.renderers.append('genshi')
base_config.default_renderer = 'kajiki'
base_config.renderers.append('kajiki')
base_config['session.enabled'] = True
base_config['session.data_serializer'] = 'json'
base_config.use_sqlalchemy = False
base_config['tm.enabled'] = False
base_config.use_ming = True
base_config.model = ksweb.model
base_config.DBSession = ksweb.model.DBSession
base_config.auth_backend = 'ming'
base_config.sa_auth.cookie_secret = "dbdcaa2e-2633-48ab-99a4-2f5d75ebdc6d"
base_config.sa_auth.user_class = model.User


class ApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def authenticate(self, environ, identity):
        login = identity['login']
        user = self.sa_auth.user_class.query.get(user_name=login)

        if not user:
            login = None
        elif not user.validate_password(identity['password']):
            login = None

        if login is None:
            from urllib.parse import parse_qs, urlencode
            from tg.exceptions import HTTPFound

            params = parse_qs(environ['QUERY_STRING'])
            params.pop('password', None)  # Remove password in case it was there
            if user is None:
                params['failure'] = 'user-not-found'
            else:
                params['login'] = identity['login']
                params['failure'] = 'invalid-password'

            # When authentication fails send user to login page.
            environ['repoze.who.application'] = HTTPFound(
                location='?'.join(('/login', urlencode(params, True)))
            )

        return login

    def get_user(self, identity, userid):
        return self.sa_auth.user_class.query.get(user_name=userid)

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]

base_config.sa_auth.authmetadata = ApplicationAuthMetadata(base_config.sa_auth)
base_config['identity.allow_missing_user'] = False
base_config.sa_auth.form_plugin = None
base_config.sa_auth.post_login_url = '/post_login'
base_config.sa_auth.post_logout_url = '/post_logout'
base_config['flash.allow_html'] = True
base_config['flash.default_status'] = 'success'
base_config['flash.template'] = '''
    <script>
        toastr.options = { "closeButton": true, "positionClass": "toast-top-right" }
        toastr.$status("$message");
    </script>
'''


from tgext import webassets
from webassets.filter import get_filter

webassets.plugme(base_config, bundles={
    'js_all': webassets.Bundle('javascript/vendors/jquery-3.3.1.min.js',
                               'javascript/vendors/toastr.min.js',
                               'javascript/vendors/popper.min.js',
                               'javascript/vendors/bootstrap.min.js',
                               'javascript/vendors/ractive.min.js',
                               'javascript/app.js',
                               filters='rjsmin', output='assets/js_all.js'),
    'css_all': webassets.Bundle('css/vendors/toastr.min.css',
                                'css/vendors/material-icons.css',
                                webassets.Bundle('css/style.scss', 
                                                 depends=('css/*.scss'), 
                                                 filters='libsass', 
                                                 output='assets_debug/style.css'),
                                filters='cssmin',
                                output='assets/css_all.css'),
    'login': webassets.Bundle(webassets.Bundle('css/login.scss', filters='libsass', output='assets_debug/login.css'),
                              filters='cssmin', output='assets/login.css'),
    'index': webassets.Bundle(webassets.Bundle('css/index.scss', filters='libsass', output='assets_debug/index.css'),
                              filters='cssmin', output='assets/index.css'),
    'new-age': webassets.Bundle(webassets.Bundle('css/vendors/new-age/new-age.scss',
                                                 filters='libsass',
                                                 output='assets_debug/new-age.css'),
                                filters='cssmin', output='assets/new-age.css')
})


from tgext.pluggable import plug
plug(base_config, 'tgext.mailer')
plug(base_config, 'registration', global_models=True)
plug(base_config, 'tgext.evolve', global_models=True, evolutions=evolutions)
from ksweb.config.registration_hooks import RegistrationHooks
RegistrationHooks.register(base_config)
plug(base_config,
     'resetpassword',
     reset_password_form='ksweb.lib.forms.ResetPasswordForm',
     new_password_form='ksweb.lib.forms.NewPasswordForm')

from tgext.pluggable import replace_template
replace_template(base_config,
                 'resetpassword.templates.index',
                 'ksweb.templates.resetpassword.index')

plug(base_config, 'userprofile')
replace_template(base_config, 'registration.templates.register', 'ksweb.templates.registration.register')
# replace_template(base_config, 'userprofile.templates.index', 'ksweb.templates.userprofile.index')
def replace_profile_form_layout():
    from axf.bootstrap import BootstrapFormLayout
    from userprofile.lib import UserForm

    UserForm.child = BootstrapFormLayout(children=UserForm.child.children)
    UserForm.submit.css_class = 'btn-primary form-control'

milestones.config_ready.register(replace_profile_form_layout)
