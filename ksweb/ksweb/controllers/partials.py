# -*- coding: utf-8 -*-
from tg import render_template


def user_menu(section=None, **kw):
    return render_template(dict(), template_name='ksweb.templates.partials.user_menu')


def sidebar(section=None, workspace=None, **kw):
    return render_template(dict(workspace=workspace), template_name='ksweb.templates.partials.sidebar')


def table(entities, fields, actions, workspace, **kw):
    return render_template(
        dict(
            fields=fields,
            entities=entities,
            actions=actions,
            workspace=workspace
        ),
        template_name='ksweb.templates.partials.table')
