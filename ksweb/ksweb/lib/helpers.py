# -*- coding: utf-8 -*-
"""Template Helpers used in ksweb."""
import logging

from bson import ObjectId
from markupsafe import Markup
from datetime import datetime

from ksweb import model

log = logging.getLogger(__name__)


def current_year():
    now = datetime.now()
    return now.strftime('%Y')


def icon(icon_name):
    return Markup('<i class="glyphicon glyphicon-%s"></i>' % icon_name)


def material_icon(icon_name):
    icon_code = {
        #  Navbar
        'delete': '&#xE872;',

        'download': '&#xE2C4;',
        'upload': '&#xE2C6;',

        'print': '&#xE8AD',
        'list': '&#xE896;',
        'arrow_back': '&#xE5C4;',
        'help_outline': '&#xE8FD;',
        'account_circle': '&#xE853',
        'label_outline': '&#xE893;',
        #  User menu
        'account_box': '&#xE851;',
        'notification_none': '&#xE7F5;',
        'exit_to_app': '&#xE879;',


        #  Sidebar
        'insert_drive_file': '&#xE24D;',
        'content_paste': '&#xE14F;',
        'flip_to_front': '&#xE883;',
        'group_work': '&#xE886;',
        'view_list': '&#xE8EF;',

        # QA
        'save': '&#xE161;',

        #  Document
        'create': '&#xE150;',

        # Mix
        'add_circle_outline': '&#xE148;',
        'add': '&#xE145;',
        'add_circle_outline_rotate': '&#xE148;',
        'add_circle': '&#xE147;',
        'remove_circle_outline': '&#xE15D;',
        'clear': '&#xE14C;',

        # Table
        'done': '&#xE876;',

        'more_horiz': '&#xE5D3;',

        
        }
    return Markup('<i class="material-icons media-middle material-icon-%s">%s</i>' % (icon_name, icon_code[icon_name]))


def table_row_content(entity, fields):
    tags = []

    # name of field that you want customize
    css_class = {
        'title': 'table-row-title'
    }
    for field in fields:
        data = getattr(entity, field)
        converters_map = {}
        if field != '_id':
            converted_value = data
            if type(data) in table_row_content.ROW_CONVERSIONS:
                converters_map = table_row_content.ROW_CONVERSIONS
                convert = converters_map.get(type(data), lambda o: o)
                converted_value = convert(data)

            elif hasattr(entity, '__ROW_TYPE_CONVERTERS__'):
                converters_map = entity.__ROW_TYPE_CONVERTERS__
                convert = converters_map.get(type(data), lambda o: o)
                converted_value = convert(data)

            elif hasattr(entity, '__ROW_COLUM_CONVERTERS__'):
                converters_map = entity.__ROW_COLUM_CONVERTERS__
                convert = converters_map.get(field, lambda o: getattr(o, field))
                converted_value = convert(entity)

        tags.append(html.HTML.td(converted_value, class_=css_class.get(field, 'table-row')))
    return html.HTML(*tags)

table_row_content.ROW_CONVERSIONS = {
    model.Category: lambda c: c.name,
    model.Precondition: lambda p: p.title,
    bool: lambda b: material_icon('done') if b else material_icon('clear'),
    model.User: lambda u: u.display_name
}


def bootstrap_pager(paginator):
    return html.HTML.div(paginator.pager(
        page_link_template='<li><a%s>%s</a></li>',
        page_plain_template='<li%s><span>%s</span></li>',
        curpage_attr={'class': 'active'}
    ), class_="pagination")


def editor_widget_template_for_output(**kw):
    # Classes explanation:
    #   objplaceholder: used by CKEDITOR for widget definition
    #   output: used for easily identify widget -> widget.hasClass('output')
    #   output-widget: used by KS for stylize (CSS) widget
    #   ks_id-output_{id_}: used for to generate unique placeholder
    return'<span class="objplaceholder output output-widget ks_id-output_{id_}">{title}</span>'.format(**kw)


def editor_widget_template_for_qa(**kw):
    # Classes explanation:
    #   objplaceholder: used by CKEDITOR for widget definition
    #   qa: used for easily identify widget -> widget.hasClass('qa')
    #   qa-widget: used by KS for stylize (CSS) widget
    #   ks_id-qa{id_}: used for to generate unique placeholder
    return '<span class="objplaceholder qa qa-widget ks_id-qa_{id_}">{title}</span>'.format(**kw)


def underscore(text):
    return text.lower().replace(" ", "_")

def gravatar(email_address, size=24):
    from hashlib import md5
    from tg import url
    mhash = md5(email_address).hexdigest()
    return url('http://www.gravatar.com/avatar/'+mhash, params=dict(s=size))

# Import commonly used helpers from WebHelpers2 and TG
from tg.util.html import script_json_encode

from ..controllers import partials

try:
    from webhelpers2 import date, html, number, misc, text
except SyntaxError:
    log.error("WebHelpers2 helpers not available with this Python Version")


def get_workspace_name(workspace_id):
    ws = model.Category.query.get(_id=ObjectId(workspace_id))
    if ws:
        return ws.name.upper()
    else:
        return 'UNKNOWN WORKSPACE'
