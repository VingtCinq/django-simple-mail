|django-simple-mail v2.0.0 on PyPi| |MIT license| |Stable|

django-simple-mail
==================

Simple customizable email template built for Django

Requirements
------------

These Django app works with :

-  Python (>=2.7) (Need to be tested for 3.x)
-  Django (>=1.9) (Need to be tested for previous versions)

Installation
------------

Install using ``pip`` :

``pip install django_simple_mail``

Add ``simple_mail`` and ``solo`` to your INSTALLED_APPS setting.

.. code:: python

    INSTALLED_APPS = (
        ...
        'simple_mail',
        'solo'
    )

Then run :

``python manage.py makemigrations`` ``python manage.py migrate``

Register mails
--------------

Create a ``mails.py`` file in your app and define your mail :

::

    from simple_mail.mailer import BaseSimpleMail, simple_mailer


    class WelcomeMail(BaseSimpleMail):
        email_key = 'welcome'


    simple_mailer.register(WelcomeMail)

Then run ``./manage.py register_mails`` to create those mail into the
database.

Send an email
-------------

You can the send the ``WelcomeEmail`` the following way :

::

    welcome_email = WelcomeEmail()
    welcome_email.set_context(args, kwargs)
    welcome_email.send(to, from_email=None, bcc=[], connection=None, attachments=[],
                       headers={}, cc=[], reply_to=[], fail_silently=False)

Preview and customization:
--------------------------

The default mail template is built with
`Cerberus <https://github.com/TedGoas/Cerberus>`__ and looks like this
with placeholder values:

.. figure:: https://raw.githubusercontent.com/charlesthk/django-simple-mail/master/docs/preview.png
   :alt: Email Preview

   Email Preview

Django Admin
------------

You can customize the colors and base content of your template directly
inside the admin.

You can manage your emails and their content directly from django admin
:

.. figure:: https://raw.githubusercontent.com/charlesthk/django-simple-mail/master/docs/admin.png
   :alt: Admin Preview

   Admin Preview

You can also use variables inside the fields to make your content more
dynamic :

.. figure:: https://raw.githubusercontent.com/charlesthk/django-simple-mail/master/docs/admin-context.png
   :alt: Admin Preview

   Admin Preview

Support
-------

If you are having issues, please let us know or submit a pull request.

License
-------

The project is licensed under the MIT License.

.. |django-simple-mail v2.0.0 on PyPi| image:: https://img.shields.io/badge/pypi-2.0.0-green.svg
   :target: https://pypi.python.org/pypi/django-simple-mail
.. |MIT license| image:: https://img.shields.io/badge/licence-MIT-blue.svg
.. |Stable| image:: https://img.shields.io/badge/status-stable-green.svg

