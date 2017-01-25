from __future__ import unicode_literals

import html2text
from django.db import models
from simple_mail.settings import sm_settings
from django.template import (Context, Template, loader)
from django.core.mail import send_mail as django_send_mail
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from premailer import transform


class SimpleMail(models.Model):
    """
    Define an email
    """
    key = models.CharField(verbose_name=_(u"Email"), choices=sm_settings.EMAILS, max_length=20, unique=True)
    subject = models.CharField(max_length=255, verbose_name=_(u"Subject"))
    title = models.CharField(max_length=255, verbose_name=_(u"Title"))
    body = models.TextField(verbose_name=_(u"Content"))
    button_label = models.CharField(verbose_name=_(u"Button label"), max_length=80, blank=True)
    button_link = models.CharField(verbose_name=_(u"Button Link"), max_length=255, blank=True)

    created_at = models.DateTimeField(verbose_name=_(u"Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_(u"Updated at"), auto_now=True)

    def __unicode__(self):
        return self.get_key_display()

    def render(self, context, template_name):
        context_temp = sm_settings.CONTEXT.copy()
        context_temp.update(context)
        context_temp.update({
            'title': Template(self.title).render(Context(context_temp)),
            'button_label': Template(self.button_label).render(Context(context_temp)),
            'button_link': Template(self.button_link).render(Context(context_temp)),
            'body': Template(self.body).render(Context(context_temp)),
        })
        if template_name is None:
            try:
                template_name = sm_settings.TEMPLATE
            except AttributeError:
                raise ImproperlyConfigured('TEMPLATE Should be configured')
        html = loader.render_to_string(template_name, context_temp)
        html = transform(html, base_url=sm_settings.BASE_URL)
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_tables = True
        text = h.handle(html)
        response = {
            'subject': Template(self.subject).render(Context(context_temp)),
            'message': text,
            'html_message': html,
        }
        return response

    def send(self, recipient_list, context={}, template_name=None, from_email=None):
        """
        Send the email
        """
        if from_email is None:
            try:
                from_email = sm_settings.FROM_EMAIL
            except AttributeError:
                raise ImproperlyConfigured('FROM_EMAIL Should be configured')
        email_kwargs = self.render(context, template_name)
        return django_send_mail(
            from_email=from_email,
            recipient_list=recipient_list,
            **email_kwargs)
