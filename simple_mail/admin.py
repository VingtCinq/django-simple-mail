from functools import update_wrapper

from django import forms
from django.contrib import admin, messages
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import PermissionDenied
from django.contrib.admin.utils import unquote
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.html import escape
from django.urls import reverse
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.admin.options import IS_POPUP_VAR
from django.template.response import TemplateResponse
from django.views.generic import RedirectView
from django.conf import settings

from simple_mail.forms import AdminSendTestMailForm
from simple_mail.models import SimpleMail, SimpleMailConfig

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class ColorInput(forms.widgets.Input):
    input_type = 'color'


def get_widgets():
    widgets = {}
    for field in SimpleMailConfig.COLOR_FIELDS:
        widgets[field] = ColorInput
    return widgets

if getattr(settings, 'SIMPLE_MAIL_USE_MODELTRANSALTION', False):
    from modeltranslation.admin import TabbedTranslationAdmin
    modelAdminClass = TabbedTranslationAdmin
else:
    modelAdminClass = admin.ModelAdmin


class SimpleMailConfigAdminForm(forms.ModelForm):
    class Meta:
        model = SimpleMailConfig
        widgets = get_widgets()
        exclude = []

class SimpleMailConfigAdmin(modelAdminClass):
    fieldsets = (
        ('Header', {
            'fields': ('logo',)
        }),
        ('Footer', {
            'fields': ('footer_content', 'facebook_url', 'twitter_url', 'instagram_url', 'website_url',)
        }),
        ('Colors', {
            'fields': SimpleMailConfig.COLOR_FIELDS,
            'classes': ('wide',)
        }),
        ('Sizings', {
            'fields': SimpleMailConfig.SIZING_FIELDS,
            'classes': ('wide',)
        }),
    )
    form = SimpleMailConfigAdminForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        try:
            from django.urls import re_path
        except ImportError:
            from django.conf.urls import url as re_path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            re_path(r'^$', wrap(RedirectView.as_view(
                pattern_name='%s:%s_%s_change' % ((self.admin_site.name,) + info)
            )), name='%s_%s_changelist' % info),
            re_path(r'^history/$', wrap(self.history_view),
                    {'object_id': str(self.singleton_instance_id)}, name='%s_%s_history' % info),
            re_path(r'^change/$', wrap(self.change_view),
                    {'object_id': str(self.singleton_instance_id)}, name='%s_%s_change' % info),
        ]
        parent_urlpatterns = super().get_urls()
        return urlpatterns + parent_urlpatterns

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if object_id == str(self.singleton_instance_id):
            self.model.objects.get_or_create(pk=self.singleton_instance_id)
        return super(SimpleMailConfigAdmin, self).change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context,
        )
    
    def response_post_save_change(self, request, obj):
        post_url = reverse('%s:app_list' % self.admin_site.name, args=(self.model._meta.app_label,))
        return HttpResponseRedirect(post_url)

    @property
    def singleton_instance_id(self):
        return getattr(self.model, 'singleton_instance_id')


admin.site.register(SimpleMailConfig, SimpleMailConfigAdmin)


class SimpleMailAdmin(modelAdminClass):
    '''
        Admin View for Mail
    '''
    list_display = ('key', 'subject',)
    readonly_fields = ('key', 'created_at', 'updated_at', 'available_context',)
    actions = None
    send_test_mail_form = AdminSendTestMailForm

    simplemail_send_test_mail_template = None
    simplemail_preview_mail_template = None

    def available_context(self, obj):
        from simple_mail.mailer import simple_mailer
        test_mail = simple_mailer._registry.get(obj.key)()
        test_mail.set_test_context()
        res = []
        for k, v in test_mail.context.items():
            res.append({
                'key': k,
                'value': v,
                'type': type(v).__name__
            })
        return loader.render_to_string('admin/simple_mail/simplemail/context.html', {'context': res})

    available_context.short_description = 'Available Context'

    fieldsets = (
        ('Content', {
            'fields': ('subject', 'title', 'body', 'banner', 'button_label', 'button_link'),
        }),
        ('Context', {
            'fields': ('available_context',),
            'classes': ('collapse',),
        }),       
        ('Metadata', {
            'fields': ('key', 'created_at', 'updated_at',),
            'classes': ('collapse',),
        }),
    )

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
        from simple_mail.mailer import simple_mailer
        test_mail = simple_mailer._registry.get(mail.key)()
        test_mail.set_test_context()
        html = test_mail.render().get('html_message')
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
                test_mail = simple_mailer._registry.get(mail.key)()
                test_mail.set_test_context()
                test_mail.send_test_mail([email])
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

        context = dict(
            self.admin_site.each_context(request),
            title= _('Send test mail: %s') % escape(mail.key),
            adminForm= adminForm,
            form_url= form_url,
            form= form,
            is_popup= (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            add= True,
            change= False,
            has_delete_permission= False,
            has_change_permission= True,
            has_absolute_url= False,
            opts= self.model._meta,
            original= mail,
            save_as= False,
            show_save= True,
        )

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.simplemail_send_test_mail_template or
            'admin/simple_mail/simplemail/send_test_mail.html',
            context,
        )

    def get_urls(self):
        try:
            from django.urls import re_path
        except ImportError:
            from django.conf.urls import url as re_path

        parent_urlpatterns = super().get_urls()

        return [
            re_path(
                r'^(?P<id>\d+)/send-test-mail/$',
                self.admin_site.admin_view(self.send_test_mail),
                name='send_test_mail',
            ),
            re_path(
                r'^(?P<id>\d+)/preview-mail/$',
                self.admin_site.admin_view(self.preview_mail),
                name='preview_mail',
            ),
        ] + parent_urlpatterns


admin.site.register(SimpleMail, SimpleMailAdmin)
