from django.core.management.base import BaseCommand, CommandError

from simple_mail.mailer import simple_mailer


class Command(BaseCommand):

    def handle(self, *args, **options):
        created_emails = simple_mailer.save_mails()
        for m in created_emails:
            print('Saving %s' % m)
        print('Successfully saved %i mails' % len(created_emails))
