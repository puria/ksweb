# -*- coding: utf-8 -*-
from tg import render_template

from ksweb.model import Output, Precondition, Document


def user_menu(section=None, **kw):
    return render_template(dict(), template_name='ksweb.templates.partials.user_menu')


def sidebar(section=None, workspace=None, **kw):
    unread_outputs = Output.unread_count(workspace)
    unread_filters = Precondition.unread_count(workspace)
    unread_documents = Document.unread_count(workspace)
    return render_template(dict(workspace=workspace,
                                unread_outputs=unread_outputs,
                                unread_filters=unread_filters,
                                unread_documents=unread_documents),
                           template_name='ksweb.templates.partials.sidebar')


def table(entities, fields, workspace, *args, **kw):
    variables = dict(fields=fields,
                     entities=entities,
                     workspace=workspace,
                     actions_content=kw.get('actions_content', None))
    variables.update(kw)

    return render_template(
        variables,
        template_name='ksweb.templates.partials.table')
