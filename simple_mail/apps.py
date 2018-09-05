from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings
from simple_mail.mailer import autodiscover


class SimpleMailConfig(AppConfig):
    name = 'simple_mail'
    verbose_name = 'Simple Mail'

    def ready(self):
        autodiscover()

        if not getattr(settings, 'SIMPLE_MAIL_LOG_CSS_WARNING', False):
            """
            By default cssutils log CSS Warning
            We prevent those logs to keep a clean log but you can
            still enable them by setting `SIMPLE_MAIL_LOG_CSS_WARNING = True`
            Snippet taken from https://gist.github.com/texuf/1e1ef7fce7aaa67caf4d
            """
            from cssutils import profile
            from cssutils.profiles import Profiles, properties, macros
            # patch um up
            properties[Profiles.CSS_LEVEL_2]['-ms-interpolation-mode'] = r'none|bicubic|nearest-neighbor'
            properties[Profiles.CSS_LEVEL_2]['-ms-text-size-adjust'] = r'none|auto|{percentage}'
            properties[Profiles.CSS_LEVEL_2]['mso-table-lspace'] = r'0|{num}(pt)'
            properties[Profiles.CSS_LEVEL_2]['mso-table-rspace'] = r'0|{num}(pt)'
            properties[Profiles.CSS_LEVEL_2]['-webkit-text-size-adjust'] = r'none|auto|{percentage}'
            # re-add
            profile.addProfiles([(Profiles.CSS_LEVEL_2,
                                  properties[Profiles.CSS_LEVEL_2],
                                  macros[Profiles.CSS_LEVEL_2]
                                  )])
