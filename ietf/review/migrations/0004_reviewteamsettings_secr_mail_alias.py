# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-03 03:10


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0003_add_notify_ad_when'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewteamsettings',
            name='secr_mail_alias',
            field=models.CharField(blank=True, help_text='Email alias for all of the review team secretaries', max_length=255, verbose_name='Email alias for all of the review team secretaries'),
        ),
    ]