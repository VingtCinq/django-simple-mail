from django import forms
from ckeditor.fields import RichTextField

from simple_mail.widgets import SimpleMailCKEditorWidget

# We override RichTextField to set ckeditor's configuration diretcly
# into the package to facilitate simple_mail's installation

class SimpleMailRichTextField(RichTextField):

    @staticmethod
    def _get_form_class():
        return SimpleMailRichTextFormField


class SimpleMailRichTextFormField(forms.fields.CharField):

    def __init__(self, config_name='default', extra_plugins=None, external_plugin_resources=None, *args, **kwargs):
        kwargs.update({'widget': SimpleMailCKEditorWidget(config_name=config_name, extra_plugins=extra_plugins,
                                                external_plugin_resources=external_plugin_resources)})
        super(SimpleMailRichTextFormField, self).__init__(*args, **kwargs)