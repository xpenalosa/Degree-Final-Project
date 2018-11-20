# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0003_objective'),
    ]

    operations = [
        migrations.AddField(
            model_name='objective',
            name='body',
            field=models.TextField(default=datetime.datetime(2018, 8, 21, 13, 24, 46, 9717, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='objective',
            name='slug',
            field=models.SlugField(max_length=16, default='tmp'),
            preserve_default=False,
        ),
    ]
