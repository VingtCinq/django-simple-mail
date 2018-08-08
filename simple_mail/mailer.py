
import os
import sys
import copy

from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import module_has_submodule
from django.apps import apps


class BaseSimpleMail(object):

    email_key = None
    template = None
    test_context = {}
    context = {}

    def __init__(self, *args, **kwargs):
        if self.email_key is None:
            raise ImproperlyConfigured('%s must have an `email_key` property.' % self.__class__.__name__)
        super(BaseSimpleMail, self).__init__(*args, **kwargs)

    def get_test_context(self):
        return self.test_context

    def get_context(self, *args, **kwargs):
        return self.test_context
    
    def set_context(self, *args, **kwargs):
        self.context = self.get_context(*args, **kwargs)

    def get_mail(self):
        from simple_mail.models import SimpleMail
        return SimpleMail.objects.get(key=self.email_key)

    def send_test_mail(self, to):
        mail = self.get_mail()
        context = self.get_test_context()
        return mail.send(to, context, self.template)

    def send(self, to, from_email=None, bcc=[],
             connection=None, attachments=[], headers={}, cc=[], reply_to=[], fail_silently=False):
        mail = self.get_mail()
        context = self.get_context()
        return mail.send(to, context, self.template, from_email, bcc,
                              connection, attachments, headers, cc, reply_to, fail_silently)
        

class AlreadyRegistered(Exception):
    pass


class SimpleMailer(object):

    _registry = {}

    def register(self, mail):
        if mail.email_key in self._registry:
            raise AlreadyRegistered('Mail "%s" is already registered' % mail.__class__.__name__)
        self._registry[mail.email_key] = mail
    
    def save_mails(self):
        from simple_mail.models import SimpleMail
        created_mails = []
        for key, value in self._registry.items():
            obj, created = SimpleMail.objects.get_or_create(key=key)
            if created:
                created_mails.append(value)
        return created_mails


simple_mailer = SimpleMailer()


def autodiscover():
    mods = [(app_config.name, app_config.module) for app_config in apps.get_app_configs()]

    for (app, mod) in mods:
        # Attempt to import the app's translation module.
        module = '%s.mails' % app
        before_import_registry = copy.copy(simple_mailer._registry)
        try:
            import_module(module)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            simple_mailer._registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an translation module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'mails'):
                raise