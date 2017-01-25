from simple_mail.models import SimpleMail

def send_mail(key, recipient_list, context={}, template_name=None, from_email=None):
    mail = SimpleMail.objects.get(key=key)
    return mail.send(recipient_list, context, template_name, from_email)
