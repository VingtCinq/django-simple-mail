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
from simple_mail.fields import SimpleMailRichTextField
from premailer import transform


class SingletonModel(models.Model):
    singleton_instance_id = 1

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = self.singleton_instance_id
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=cls.singleton_instance_id)
        return obj


@python_2_unicode_compatible
class SimpleMailConfig(SingletonModel):

    TITLE_SIZE_H1 = 'h1'
    TITLE_SIZE_H2 = 'h2'
    TITLE_SIZE_H3 = 'h3'
    TITLE_SIZE_CHOICES = (
        (TITLE_SIZE_H1, 'h1'),
        (TITLE_SIZE_H2, 'h2'),
        (TITLE_SIZE_H3, 'h3'),
    )

    # General
    base_url = models.URLField(verbose_name=_("Base url"), max_length=255, default="http://localhost:8000")
    from_email = models.EmailField(verbose_name=_("From Email"), max_length=255, default="webmaster@localhost")
    from_name = models.CharField(verbose_name=_("From Name"), max_length=255, default="Company Inc")
    # Header
    logo = models.ImageField(verbose_name=_("Logo"), upload_to="simple_mail", blank=True, null=True)
    # footer
    footer_content = SimpleMailRichTextField(config_name="simple_mail_b", verbose_name=_("Footer"), blank=True)
    facebook_url = models.URLField(verbose_name=_("Facebook Url"), max_length=255, blank=True)
    twitter_url = models.URLField(verbose_name=_("Twitter Url"), max_length=255, blank=True)
    instagram_url = models.URLField(verbose_name=_("Instagram Url"), max_length=255, blank=True)
    website_url = models.URLField(verbose_name=_("Website Url"), max_length=255, blank=True)
    # Colors
    ## header
    color_header_bg = models.CharField(verbose_name=_("Header background"), max_length=7, default="#F7F7F7")
    color_title = models.CharField(verbose_name=_("Body title"), max_length=7, default="#222222")
    title_size = models.CharField(verbose_name=_("Title size"), max_length=2, choices=TITLE_SIZE_CHOICES, default=TITLE_SIZE_H1)
    ## body
    color_body_bg = models.CharField(verbose_name=_("Body background"), max_length=7, default="#FFFFFF")
    color_body = models.CharField(verbose_name=_("Body content"), max_length=7, default="#808080")
    color_body_link = models.CharField(verbose_name=_("Body links"), max_length=7, default="#007E9E")
    ## button
    color_button = models.CharField(verbose_name=_("Button content"), max_length=7, default="#FFFFFF")
    color_button_bg = models.CharField(verbose_name=_("Button background"), max_length=7, default="#00ADD8")
    border_radius_button = models.PositiveSmallIntegerField(verbose_name=_("Button border radius"), default=3)
    ## footer
    color_footer = models.CharField(verbose_name=_("Footer content"), max_length=7, default="#FFFFFF")
    color_footer_link = models.CharField(verbose_name=_("Footer Link"), max_length=7, default="#FFFFFF")
    color_footer_bg = models.CharField(verbose_name=_("Footer background"), max_length=7, default="#333333")
    color_footer_divider = models.CharField(verbose_name=_("Footer divider"), max_length=7, default="#505050")

    resized_logo = ImageSpecField(source='logo',
                                  processors=[ResizeToFit(392, None)],
                                  format='JPEG',
                                  options={'quality': 90})

    COLOR_FIELDS = ['color_header_bg', 'color_title', 'color_body_bg', 'color_body', 'color_body_link',
                    'color_button', 'color_button_bg', 'color_footer', 'color_footer_link', 'color_footer_bg',
                    'color_footer_divider']
    
    SIZING_FIELDS = ['border_radius_button', 'title_size']

    def __str__(self):
        return 'Simple Mail Configuration'

    @property
    def context(self):
        return {
            'logo_url': self.logo_url,
            'footer_content': self.footer_content,
            'facebook_url': self.facebook_url,
            'twitter_url': self.twitter_url,
            'instagram_url': self.instagram_url,
            'website_url': self.website_url,
            'color_header_bg': self.color_header_bg,
            'color_title': self.color_title,
            'title_size': self.title_size,
            'color_body_bg': self.color_body_bg,
            'color_body': self.color_body,
            'color_body_link': self.color_body_link,
            'color_button': self.color_button,
            'color_button_bg': self.color_button_bg,
            'color_footer': self.color_footer,
            'color_footer_divider': self.color_footer_divider,
            'color_footer_link': self.color_footer_link,
            'color_footer_bg': self.color_footer_bg,
            'border_radius_button': self.border_radius_button,
        }

    @property
    def logo_url(self):
        if self.logo:
            return self.resized_logo.url
        return None

    @property
    def from_(self):
        return "{from_name} <{from_email}>".format(from_name=self.from_name, from_email=self.from_email)

    class Meta:
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configuration'


@python_2_unicode_compatible
class SimpleMail(models.Model):
    """
    Define an email
    """
    key = models.CharField(verbose_name=_("Email Key"), editable=False, max_length=100, unique=True)
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    title = models.CharField(max_length=255, verbose_name=_("Title"), blank=True)
    body = SimpleMailRichTextField(config_name="simple_mail_p", verbose_name=_("Content"))
    banner = models.ImageField(verbose_name=_("Banner"), upload_to="simple_mail", blank=True, null=True)
    button_label = models.CharField(verbose_name=_("Button label"), max_length=80, blank=True)
    button_link = models.CharField(verbose_name=_("Button Link"), max_length=255, blank=True)

    resized_banner = ImageSpecField(source='banner',
                                    processors=[ResizeToFit(1128, None)],
                                    format='JPEG',
                                    options={'quality': 90})

    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)
    
    def __str__(self):
        return self.key

    @property
    def banner_url(self):
        if self.banner:
            return self.resized_banner.url
        return None

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def render(self, context={}, template=None):
        config = SimpleMailConfig.get_singleton()
        base_context = config.context
        base_context['banner_url'] = self.banner_url
        base_context.update(context)
        subject = Template(self.subject).render(Context(base_context))
        base_context.update({
            'title': Template(self.title).render(Context(base_context)),
            'subject': subject,
            'footer_content': Template(base_context.get('footer_content')).render(Context(base_context)),
            'button_label': Template(self.button_label).render(Context(base_context)),
            'button_link': Template(self.button_link).render(Context(base_context)),
            'body': Template(self.body).render(Context(base_context)),
        })
        if template is None:
            template = getattr(settings, 'SIMPLE_MAIL_DEFAULT_TEMPLATE', 'simple_mail/default.html')
        html = loader.render_to_string(template, base_context)
        html = transform(html, base_url=config.base_url)
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_tables = True
        text = h.handle(html)
        response = {
            'subject': subject,
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

