# -*- coding: utf-8 -*-
import tg
from ksweb.model import Group


class RegistrationHooks(object):
    @classmethod
    def register(cls, base_config):
        tg.hooks.register('registration.before_activation', cls.before_activation)

    @staticmethod
    def before_activation(registration, user):
        #  In accord to  4.7 - Ticket every new user must be set to lawyer groups.
        lawyer_group = Group.query.find({'group_name': 'lawyer'}).first()
        user.groups = [lawyer_group]
