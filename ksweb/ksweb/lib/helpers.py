# -*- coding: utf-8 -*-
"""Template Helpers used in ksweb."""
import logging
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
        'account_circle': '&#xE853',

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
        'add_circle_outline': '&#xE148;',

        # Table
        'done': '&#xE876;',
        'clear': '&#xE14C;',
        'more_horiz': '&#xE5D3;'

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
            if type(data) in table_row_content.ROW_CONVERSIONS:
                converters_map = table_row_content.ROW_CONVERSIONS
            elif hasattr(entity, '__ROW_CONVERTERS__'):
                converters_map = entity.__ROW_CONVERTERS__
        convert = converters_map.get(type(data), lambda o: o)
        tags.append(html.HTML.td(convert(data), class_=css_class.get(field, 'table-row')))
    return html.HTML(*tags)
table_row_content.ROW_CONVERSIONS = {
    model.Category: lambda c: c.name,
    bool: lambda b: material_icon('done') if b else material_icon('clear')

}

def bootstrap_pager(paginator):
    return html.HTML.div(paginator.pager(
        page_link_template='<li><a%s>%s</a></li>',
        page_plain_template='<li%s><span>%s</span></li>',
        curpage_attr={'class': 'active'}
    ), class_="pagination")


# Import commonly used helpers from WebHelpers2 and TG
from tg.util.html import script_json_encode

from ..controllers import partials

try:
    from webhelpers2 import date, html, number, misc, text
except SyntaxError:
    log.error("WebHelpers2 helpers not available with this Python Version")

