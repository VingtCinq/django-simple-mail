from simple_mail.models import SimpleMail

def send_mail(key, to, context={}, template_name=None, from_email=None, bcc=[],
             connection=None, attachments=[], headers={}, cc=[], reply_to=[], fail_silently=False):
    mail = SimpleMail.objects.get(key=key)
    return mail.send_mail(to, context, template_name, from_email, bcc,
                         connection, attachments, headers, cc, reply_to, fail_silently)
