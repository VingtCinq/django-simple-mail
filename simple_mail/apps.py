from __future__ import unicode_literals

from django.apps import AppConfig

from simple_mail.mailer import autodiscover


class SimpleMailConfig(AppConfig):
    name = 'simple_mail'

    def ready(self):
        autodiscover()