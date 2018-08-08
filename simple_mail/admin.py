from django.contrib import admin, messages
from simple_mail.models import SimpleMail, SimpleMailConfig
from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import PermissionDenied
from django.contrib.admin.utils import unquote
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.html import escape
from django.urls import path, reverse
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.admin.options import IS_POPUP_VAR
from django.template.response import TemplateResponse

from simple_mail.forms import AdminSendTestMailForm
from solo.admin import SingletonModelAdmin

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

from django import forms

class ColorInput(forms.TextInput):
    input_type = 'color'


class SimpleMailConfigAdminForm(forms.ModelForm):
    class Meta:
        model = SimpleMailConfig
        widgets = {
            'color_bg': ColorInput,
            'color_container_bg': ColorInput,
            'color_container_border': ColorInput,
            'color_title': ColorInput,
            'color_content': ColorInput,
            'color_footer': ColorInput,
            'color_footer_bg': ColorInput,
            'color_button': ColorInput,
            'color_button_bg': ColorInput,
        }
        exclude = []

class SimpleMailConfigAdmin(SingletonModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('base_url', 'from_email', 'from_name',)
        }),
        ('Header', {
            'fields': ('header',)
        }),
        ('Footer', {
            'fields': ('footer_content',)
        }),
        ('Colors', {
            'fields': ('color_bg', 'color_container_bg', 'color_container_border', 'color_title', 'color_content', 'color_footer', 'color_footer_bg', 'color_button', 'color_button_bg',),
        }),
    )
    form = SimpleMailConfigAdminForm

admin.site.register(SimpleMailConfig, SimpleMailConfigAdmin)


class SimpleMailAdmin(admin.ModelAdmin):
    '''
        Admin View for Mail
    '''
    list_display = ('key', 'subject',)
    readonly_fields = ('key',)
    send_test_mail_form = AdminSendTestMailForm

    simplemail_send_test_mail_template = None
    simplemail_preview_mail_template = None

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def preview_mail(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        mail = self.get_object(request, unquote(id))
        if mail is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        html = mail.render().get('html_message')
        return HttpResponse(html)


    @sensitive_post_parameters_m
    def send_test_mail(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        mail = self.get_object(request, unquote(id))
        if mail is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.send_test_mail_form(request.POST)
            if form.is_valid():
                from simple_mail.mailer import simple_mailer
                email = form.cleaned_data.get('email')
                test_mail = simple_mailer._registry.get(mail.key)
                test_mail().send_test_mail([email])
                msg = gettext('Test mail successfully sent.')
                messages.success(request, msg)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            mail._meta.app_label,
                            mail._meta.model_name,
                        ),
                        args=(mail.pk,),
                    )
                )
        else:
            form = self.send_test_mail_form()

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Send test mail: %s') % escape(mail.key),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': mail,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.simplemail_send_test_mail_template or
            'admin/simple_mail/send_test_mail.html',
            context,
        )

    def get_urls(self):
        return [
            path(
                '<id>/send-test-mail/',
                self.admin_site.admin_view(self.send_test_mail),
                name='send_test_mail',
            ),
            path(
                '<id>/preview-mail/',
                self.admin_site.admin_view(self.preview_mail),
                name='preview_mail',
            ),
        ] + super().get_urls()

admin.site.register(SimpleMail, SimpleMailAdmin)