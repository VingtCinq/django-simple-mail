from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError

from simple_mail.mailer import simple_mailer


class Command(BaseCommand):

    def handle(self, *args, **options):
        deleted_emails = simple_mailer.delete_mails()
        for m in deleted_emails:
            print('Delete %s' % m)
        print('Successfully deleted %i mails' % len(deleted_emails))
