from __future__ import unicode_literals

import html2text

from django.db import models
from django.conf import settings
from django.template import (Context, Template, loader)
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from pilkit.processors import ResizeToFit
from imagekit.models import ImageSpecField
from solo.models import SingletonModel
from premailer import transform


@python_2_unicode_compatible
class SimpleMailConfig(SingletonModel):
    base_url = models.URLField(verbose_name=_("Base url"), max_length=255, default="http://localhost:8000")
    from_email = models.EmailField(verbose_name=_("From Email"), max_length=255, default="webmaster@localhost")
    from_name = models.CharField(verbose_name=_("From Name"), max_length=255, default="Company Inc")
    header = models.ImageField(verbose_name=_("Header"), upload_to="simple_mail", blank=True, null=True)
    footer_content = models.TextField(verbose_name=_("Footer content"), blank=True, default="")
    color_bg = models.CharField(verbose_name=_("Background"), max_length=7, default="#FFFFFF")
    color_container_bg = models.CharField(verbose_name=_("Container background"), max_length=7, default="#FFFFFF")
    color_container_border = models.CharField(verbose_name=_("Container border"), max_length=7, default="#CCCCCC")
    color_title = models.CharField(verbose_name=_("Title"), max_length=7, default="#2C9AB7")
    color_content = models.CharField(verbose_name=_("Text"), max_length=7, default="#444444")
    color_footer = models.CharField(verbose_name=_("Footer"), max_length=7, default="#CCCCCC")
    color_footer_bg = models.CharField(verbose_name=_("Footer background"), max_length=7, default="#555555")
    color_button = models.CharField(verbose_name=_("Button"), max_length=7, default="#FFFFFF")
    color_button_bg = models.CharField(verbose_name=_("Button background"), max_length=7, default="#2C9AB7")

    resized_header = ImageSpecField(source='header',
                                    processors=[ResizeToFit(1200, None)],
                                    format='JPEG',
                                    options={'quality': 90})

    def __str__(self):
        return 'Simple Mail Configuration'

    @property
    def context(self):
        return {
            'header_url': self.header_url,
            'footer_content': self.footer_content,
            'color_bg': self.color_bg,
            'color_container_bg': self.color_container_bg,
            'color_container_border': self.color_container_border,
            'color_title': self.color_title,
            'color_content': self.color_content,
            'color_footer': self.color_footer,
            'color_footer_bg': self.color_footer_bg,
            'color_button': self.color_button,
            'color_button_bg': self.color_button_bg
        }

    @property
    def header_url(self):
        if self.header:
            return self.resized_header.url
        else:
            return "http://placehold.it/1200x300"

    @property
    def from_(self):
        return "{from_name} <{from_email}>".format(from_name=self.from_name, from_email=self.from_email)

    class Meta:
        verbose_name = 'Email Config'


@python_2_unicode_compatible
class SimpleMail(models.Model):
    """
    Define an email
    """
    key = models.CharField(verbose_name=_("Email Key"), editable=False, max_length=20, unique=True)
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    body = models.TextField(verbose_name=_("Content"))
    button_label = models.CharField(verbose_name=_("Button label"), max_length=80, blank=True)
    button_link = models.CharField(verbose_name=_("Button Link"), max_length=255, blank=True)

    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)
    
    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def render(self, context={}, template=None):
        config = SimpleMailConfig.get_solo()
        base_context = config.context
        base_context.update(context)
        base_context.update({
            'title': Template(self.title).render(Context(base_context)),
            'button_label': Template(self.button_label).render(Context(base_context)),
            'button_link': Template(self.button_link).render(Context(base_context)),
            'body': Template(self.body).render(Context(base_context)),
        })
        if template is None:
            template = getattr(settings, 'SIMPLE_MAIL_TEMPLATE', 'simple_mail/default.html')
        html = loader.render_to_string(template, base_context)
        html = transform(html, base_url=config.base_url)
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_tables = True
        text = h.handle(html)
        response = {
            'subject': Template(self.subject).render(Context(base_context)),
            'message': text,
            'html_message': html,
            'from_email': config.from_
        }
        return response

    def get_email_message(self, to, context={}, template=None, from_email=None, bcc=[],
                          connection=None, attachments=[], headers={}, cc=[], reply_to=[]):
        email_kwargs = self.render(context, template)
        if from_email is None:
            from_email = email_kwargs.get('from_email')
        email_message = EmailMultiAlternatives(
            subject=email_kwargs.get('subject'),
            body=email_kwargs.get('message'),
            from_email=from_email,
            to=to,
            bcc=bcc,
            connection=connection,
            attachments=attachments,
            headers=headers,
            cc=cc,
            reply_to=reply_to
        )
        email_message.attach_alternative(email_kwargs.get('html_message'), "text/html")
        return email_message

    def send(self, to, context={}, template=None, from_email=None, bcc=[],
             connection=None, attachments=[], headers={}, cc=[], reply_to=[], fail_silently=False):
        """
        Send the email with the template corresponding to `template`
        """
        email_message = self.get_email_message(to, context, template, from_email, bcc, connection, attachments, headers, cc, reply_to)
        return email_message.send(fail_silently=fail_silently)

    def send_mass_mail(self, to, context={}, template=None, from_email=None, bcc=[],
                       connection=None, attachments=[], headers={}, cc=[], reply_to=[],
                       fail_silently=False, auth_user=None, auth_password=None):
        """
        Send the same email with the template corresponding to `template` to each recipient in `to`independently
        """
        connection = connection or get_connection(
            username=auth_user,
            password=auth_password,
            fail_silently=fail_silently
        )
        messages = [
            self.get_email_message([recipient], context, template, from_email, bcc, connection, attachments, headers, cc, reply_to)
            for recipient in to
        ]
        return connection.send_messages(messages)

