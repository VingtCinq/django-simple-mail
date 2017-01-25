from django.contrib import admin
from simple_mail.models import SimpleMail
from django.contrib import admin


class SimpleMailAdmin(admin.ModelAdmin):
    '''
        Admin View for Mail
    '''
    list_display = ('key',)

admin.site.register(SimpleMail, SimpleMailAdmin)