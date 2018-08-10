from django import forms
from django.db import models
from django.conf import settings

if getattr(settings, 'SIMPLE_MAIL_USE_CKEDITOR', False):

    from ckeditor.fields import RichTextField
    from simple_mail.widgets import SimpleMailCKEditorWidget
    # We override RichTextField to set ckeditor's configuration diretcly
    # into the package to facilitate simple_mail's installation

    class SimpleMailRichTextFormField(forms.fields.CharField):

        def __init__(self, config_name='default', extra_plugins=None, external_plugin_resources=None, *args, **kwargs):
            kwargs.update({'widget': SimpleMailCKEditorWidget(config_name=config_name, extra_plugins=extra_plugins,
                                                    external_plugin_resources=external_plugin_resources)})
            super(SimpleMailRichTextFormField, self).__init__(*args, **kwargs)

    class SimpleMailRichTextField(RichTextField):

        @staticmethod
        def _get_form_class():
            return SimpleMailRichTextFormField

else:

    class SimpleMailRichTextField(models.TextField):

        def __init__(self, *args, **kwargs):
            self.config_name = kwargs.pop("config_name", "default")
            super(SimpleMailRichTextField, self).__init__(*args, **kwargs)