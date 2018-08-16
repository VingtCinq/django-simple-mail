from ckeditor.widgets import CKEditorWidget, DEFAULT_CONFIG


SIMPLE_MAIL_CKEDITOR_CONFIGS = {
    'simple_mail_b': {
        'toolbar': 'simple_mail_b',
        'toolbar_simple_mail_b': [
            ['Bold', 'Italic', 'Underline'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'autoParagraph': False,
        'shiftEnterMode': 2,
        'enterMode': 2,
        'entities': False,
        'removeDialogTabs': 'link:advanced'
    },
    'simple_mail_p': {
        'toolbar': 'simple_mail_p',
        'toolbar_simple_mail_p': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'autoParagraph': False,
        'shiftEnterMode': 2,
        'enterMode': 1,
        'entities': False,
        'removeDialogTabs': 'link:advanced'
    }
}


class SimpleMailCKEditorWidget(CKEditorWidget):

    def __init__(self, config_name='default', extra_plugins=None, external_plugin_resources=None, *args, **kwargs):
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = DEFAULT_CONFIG.copy()

        # Try to get valid config from settings.
        configs = SIMPLE_MAIL_CKEDITOR_CONFIGS
        if configs:
            if isinstance(configs, dict):
                # Make sure the config_name exists.
                if config_name in configs:
                    config = configs[config_name]
                    # Make sure the configuration is a dictionary.
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] \
                                setting must be a dictionary type.' %
                                                   config_name)
                    # Override defaults with settings config.
                    self.config.update(config)
                else:
                    raise ImproperlyConfigured("No configuration named '%s' \
                            found in your CKEDITOR_CONFIGS setting." %
                                               config_name)
            else:
                raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a\
                        dictionary type.')

        extra_plugins = extra_plugins or []

        if extra_plugins:
            self.config['extraPlugins'] = ','.join(extra_plugins)

        self.external_plugin_resources = external_plugin_resources or []