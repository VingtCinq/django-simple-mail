from django.conf import settings

if getattr(settings, 'SIMPLE_MAIL_USE_MODELTRANSALTION', False):
    from modeltranslation.translator import translator, TranslationOptions
    from simple_mail.models import SimpleMailConfig, SimpleMail


    class SimpleMailConfigTranslationOptions(TranslationOptions):
        fields = ('footer_content',)

    translator.register(SimpleMailConfig, SimpleMailConfigTranslationOptions)


    class SimpleMailTranslationOptions(TranslationOptions):
        fields = ('subject', 'title', 'body', 'button_label', 'button_link',)

    translator.register(SimpleMail, SimpleMailTranslationOptions)