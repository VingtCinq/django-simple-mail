# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SimpleMail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[[b'SUBSCRIPTION', b"Utilisateur - Demande d'inscription"], [b'WELCOME', b'Utilisateur - Bienvenu chez mailedit'], [b'RESET_PASSWORD', b'Utilisateur - R\xc3\xa9initialisation de mot de passe'], [b'USER_PROJECT_SUBM', b'Utilisateur - Votre demande de devis sur mailedit'], [b'ADMIN_PROJECT_SUBM', b'Administrateur - Nouvelle demande de devis re\xc3\xa7ue'], [b'USER_PROJECT_QUOTE', b'Utilisateur - Votre devis sur mailedit'], [b'USER_PROJECT_ORDER', b'Utilisateur - Confirmation de votre commande sur mailedit'], [b'ADMIN_PROJECT_ORDER', b'Administrateur - Nouvelle commande'], [b'USER_PROJECT_PROD', b'Utilisateur - Votre commande est mise en production sur mailedit'], [b'USER_PROJECT_DELVRY', b'Utilisateur - Votre commande a \xc3\xa9t\xc3\xa9 exp\xc3\xa9di\xc3\xa9e'], [b'USER_PROJECT_BILL', b'Utilisateur - Une nouvelle facture a \xc3\xa9t\xc3\xa9 \xc3\xa9mise'], [b'ADMIN_PROJECT_BILL', b'Administrateur - Une nouvelle facture a \xc3\xa9t\xc3\xa9 \xc3\xa9mise']], max_length=20, unique=True, verbose_name='Email')),
                ('subject', models.CharField(max_length=255, verbose_name='Subject')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('body', models.TextField(verbose_name='Content')),
                ('button_label', models.CharField(blank=True, max_length=80, verbose_name='Button label')),
                ('button_link', models.CharField(blank=True, max_length=255, verbose_name='Button Link')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
        ),
    ]
