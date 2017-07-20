# -*- coding: utf-8 -*-
##############################################################################
#
#    Knowledge Shaper, Collaborative knowledge tools editor
#    Copyright (c) 2017-TODAY StudioLegale.it <http://studiolegale.it>
#                             AXANT.it <http://axant.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from ksweb.controllers.output_plus import OutputPlusController
from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from ksweb import model
from bson import ObjectId
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
    output_plus = OutputPlusController()

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "ksweb"

    @expose('ksweb.templates.index')
    @require(predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer')))
    def index(self):
        user = request.identity['user']
        categories = model.Category.query.find({'visible': True}).sort('_id').all()
        return dict(page='index', user=user, workspaces=categories, show_sidebar=False)

    @expose('ksweb.templates.welcome')
    @require(predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer')))
    def welcome(self, workspace):
        user = request.identity['user']
        ws = model.Category.query.find({'_id': ObjectId(workspace)}).first()
        return dict(page='welcome', user=user, workspace=workspace, ws=ws, show_sidebar=True)

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
