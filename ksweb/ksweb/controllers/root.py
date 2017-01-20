# -*- coding: utf-8 -*-
"""Main Controller"""
import tg
from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from ksweb import model
from tgext.admin.mongo import BootstrapTGMongoAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from ksweb.controllers.category import CategoryController
from ksweb.controllers.document import DocumentController
from ksweb.controllers.output import OutputController
from ksweb.controllers.precondition.precondition import PreconditionController
from ksweb.controllers.qa import QaController
from ksweb.controllers.questionary import QuestionaryController
from ksweb.lib.base import BaseController
from ksweb.controllers.error import ErrorController
from ksweb.controllers.resolve import ResolveController

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the ksweb application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    admin = AdminController(model, None, config_type=TGAdminConfig)
    qa = QaController()
    precondition = PreconditionController()
    category = CategoryController()
    output = OutputController()
    document = DocumentController()
    questionary = QuestionaryController()
    resolve = ResolveController()

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "ksweb"

    @expose('ksweb.templates.index')
    @require(predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer')))
    def index(self):
        """Handle the front-page."""
        return dict(page='index')


    @expose('ksweb.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)


    @expose('ksweb.templates.document.poc')
    def add_document(self, **kw):
        from ksweb.model import Document, Category

        print "--->", kw.get('document_editor')

        d = Document(
            _owner=request.identity['user']._id,
            _category=Category.query.find({}).all()[0]._id,
            title='Documento dall \'editor',
            content={},
            text=kw.get('document_editor')
        )

        return dict(document=d)
