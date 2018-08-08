"""
Settings for PDF Generator are all namespaced in the SIMPLE_MAIL setting.
For example your project's `settings.py` file might look like this:

SIMPLE_MAIL = {
    'CONTEXT': {
        'header_url': 'http://placehold.it/1200x300',
        'footer_content': "",
        'colors': {
            'background': "#FFFFFF",
            'container_bg': "#FFFFFF",
            'container_border': "#CCCCCC",
            'title': "#2C9AB7",
            'content': "#444444",
            'footer': "#888888",
            'footer_bg': "#555555",
            'button': "#FFFFFF",
            'button_bg': "#2C9AB7",
        }
    },
    'TEMPLATE': 'simple_mail/default.html',
    'EMAIL_TO': '',
    'EMAILS': [],
    'BASE_URL': '',
    'FROM_EMAIL': ''
}

This module provides the `sm_settings` object, that is used to access
Simple Mail settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals
import os
import collections
import six
from django.conf import settings
from django.test.signals import setting_changed



def dict_nested_update(d, u):
    """
    update values of nested dictionaries keys
    taken from http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            r = dict_nested_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


DEFAULTS = {
    'CONTEXT': {
        'header_url': 'http://placehold.it/1200x300',
        'footer_content': "",
        'colors': {
            'background': "#FFFFFF",
            'container_bg': "#FFFFFF",
            'container_border': "#CCCCCC",
            'title': "#2C9AB7",
            'content': "#444444",
            'footer': "#888888",
            'footer_bg': "#555555",
            'button': "#FFFFFF",
            'button_bg': "#2C9AB7",
        }
    },
    'TEMPLATE': 'simple_mail/default.html',
    'EMAIL_TO': '',
    'EMAILS': [],
    'BASE_URL': '',
    'FROM_EMAIL': ''
}


class SimpleMailSettings(object):
    """
    A settings object, that allows SIMPLE MAIL settings to be accessed as properties.
    For example:
        from simple_mail.settings import sm_settings
        print(sm_settings.TEMPLATE)
    """
    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'SIMPLE_MAIL', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Simple Mail setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]
        else:
            # Since all keys of CONTEXT are mandatory
            # Update the user provided value with
            # potential missing keys
            if attr == 'CONTEXT':
                val = dict_nested_update(self.defaults[attr].copy(), val)
        # Cache the result
        setattr(self, attr, val)
        return val


sm_settings = SimpleMailSettings(None, DEFAULTS)


def reload_sm_settings(*args, **kwargs):
    global sm_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'SIMPLE_MAIL':
        sm_settings = SimpleMailSettings(value, DEFAULTS)


setting_changed.connect(reload_sm_settings)
