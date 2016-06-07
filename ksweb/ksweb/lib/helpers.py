# -*- coding: utf-8 -*-
"""Template Helpers used in ksweb."""
import logging
from markupsafe import Markup
from datetime import datetime
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

        }
    return Markup('<i class="material-icons media-middle">'+icon_code[icon_name]+'</i>')


# Import commonly used helpers from WebHelpers2 and TG
from tg.util.html import script_json_encode

from ..controllers import partials

try:
    from webhelpers2 import date, html, number, misc, text
except SyntaxError:
    log.error("WebHelpers2 helpers not available with this Python Version")

