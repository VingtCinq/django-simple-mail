|django-simple-mail v2.1.2 on PyPi| |MIT license| |Stable|

django-simple-mail
==================

Simple customizable email template built for Django

The 2.\* versions have breaking changes from the 1.\* and are not
backward compatible.

Template preview
----------------

The base template was built with `Mailchimp <https://mailchimp.com/>`__
editor :

.. figure:: https://raw.githubusercontent.com/charlesthk/django-simple-mail/master/docs/preview.png
   :alt: Email Preview

   Email Preview

Requirements
------------

This Django app works with :

-  Python (>=2.7)
-  Django (>=1.9) (Need to be tested for previous versions)

Todo
----

-  Write tests
-  validate compatibility with previous versions of Django and Python
-  Set a demo app on pythonanywhere

Installation
------------

Install using ``pip`` :

``pip install django_simple_mail``

Add ``simple_mail`` to your INSTALLED_APPS settings.

.. code:: python

    INSTALLED_APPS = (
        ...
        'simple_mail',
        ...
    )

Then run :

``python manage.py migrate``

Integrations
------------

CKEDITOR for a WYSIWYG edition of contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple Mail easily integrates with ``django-ckeditor`` to have a wysiwyg
edition of content. To use it :

``pip install django-ckeditor``

Then add ``ckeditor`` to your INSTALLED_APPS settings.

.. code:: python

    INSTALLED_APPS = (
        ...
        'ckeditor',
        ...
    )

And set the following in your settings :

``SIMPLE_MAIL_USE_CKEDITOR = True``

ModelTranslation to translate emails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple Mail easily integrates with ``django-modeltranslation`` to get
the content of your emails available in multiple languages.

``pip install django-modeltranslation``

Then add ``modeltranslation`` to your INSTALLED_APPS settings.

.. code:: python

    INSTALLED_APPS = (
        ...
        'modeltranslation',
        ...
    )

And set the following in your settings :

``SIMPLE_MAIL_USE_MODELTRANSALTION = True``

And run :

``python manage.py sync_translation_fields``

Create, register and send mails
-------------------------------

Register Mail
~~~~~~~~~~~~~

Create a ``mails.py`` file in your app and define your mail.

The ``email_key`` attribute must not exceed 100 characters.

.. code:: python

    from simple_mail.mailer import BaseSimpleMail, simple_mailer


    class WelcomeMail(BaseSimpleMail):
        email_key = 'welcome'


    simple_mailer.register(WelcomeMail)

Then run ``./manage.py register_mails`` to create those mail into the
database.

The mail with key ``welcome`` will he be available for edition in your
django admin.

Send an email
~~~~~~~~~~~~~

You can the send the ``WelcomeMail`` the following way :

.. code:: python

    welcome_mail = WelcomeMail()
    welcome_mail.send(to, from_email=None, bcc=[], connection=None, attachments=[],
                       headers={}, cc=[], reply_to=[], fail_silently=False)

Passing variables to email
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass variable to email with the ``context`` attribute :

.. code:: python

    from simple_mail.mailer import BaseSimpleMail, simple_mailer


    class WelcomeMail(BaseSimpleMail):
        email_key = 'welcome'
        context = {
            'title' : 'My email title',
            'user': 'the user'
        }


    simple_mailer.register(WelcomeMail)

Or you can create a ``set_context`` method:

.. code:: python

    from simple_mail.mailer import BaseSimpleMail, simple_mailer


    class WelcomeMail(BaseSimpleMail):
        email_key = 'welcome'

        def set_context(self, user_id, welcome_link):
            user = User.objects.get(id=user_id)
            self.context = {
                'user': user,
                'welcome_link': welcome_link
            }


    simple_mailer.register(WelcomeMail)

You will then need to call the ``set_context`` before sending an email:

.. code:: python

    welcome_mail = WelcomeMail()
    welcome_mail.set_context(user_id, welcome_link)
    welcome_mail.send(to, from_email=None, bcc=[], connection=None, attachments=[],
                       headers={}, cc=[], reply_to=[], fail_silently=False)

Email preview and test email
----------------------------

From the admin you can preview an email and send a test email.

Both methods use your ``context`` attribute to render the email.

If you use the ``set_context`` method, you might need to create a
``set_test_context`` method.

This method should not take any argument :

.. code:: python

    from simple_mail.mailer import BaseSimpleMail, simple_mailer


    class WelcomeMail(BaseSimpleMail):
        email_key = 'welcome'

        def set_context(self, user_id, welcome_link):
            user = User.objects.get(id=user_id)
            self.context = {
                'user': user,
                'welcome_link': welcome_link
            }
        
        def set_test_context(self):
            user_id = User.objects.order_by('?').first().id
            self.set_context(user_id, 'http://my-webiste.com/my-path')


    simple_mailer.register(WelcomeMail)

This method impact the fields displayed in the **Context** section of
the admin.

Mail configuration & edition
----------------------------

Customize your base content and template colors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You change the look and feel or your template directly from the django
admin : The **Footer** field can use template tags and variables.

.. figure:: https://raw.githubusercontent.com/charlesthk/django-simple-mail/master/docs/admin-mail-template-configuration.png
   :alt: Admin mail configuration

   Admin mail configuration

Edit the content of each of your mail :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can edit the content of each of your mail. The **Content**,
**Subject**, **button label** and **button link** fields can use
template tags and variables.

.. figure:: https://raw.githubusercontent.com/charlesthk/django-simple-mail/master/docs/admin-mail-edition.png
   :alt: Admin mail edition

   Admin mail edition

Custom template
---------------

You can define your own email template :

By setting a ``template`` attribute from you
``BaseSimpleMail``\ subclass :

.. code:: python

    from simple_mail.mailer import BaseSimpleMail, simple_mailer


    class WelcomeMail(BaseSimpleMail):
        email_key = 'welcome'
        template = 'my_app/my_email_template.html'


    simple_mailer.register(WelcomeMail)

Or by setting ``SIMPLE_MAIL_DEFAULT_TEMPLATE`` in your settings :

.. code:: python

    SIMPLE_MAIL_DEFAULT_TEMPLATE = 'my_app/my_email_template.html'

Support
-------

If you are having issues, please let us know or submit a pull request.

License
-------

The project is licensed under the MIT License.

.. |django-simple-mail v2.1.2 on PyPi| image:: https://img.shields.io/badge/pypi-2.1.2-green.svg
   :target: https://pypi.python.org/pypi/django-simple-mail
.. |MIT license| image:: https://img.shields.io/badge/licence-MIT-blue.svg
.. |Stable| image:: https://img.shields.io/badge/status-stable-green.svg

