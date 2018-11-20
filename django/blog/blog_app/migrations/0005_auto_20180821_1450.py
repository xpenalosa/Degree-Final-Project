# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0004_auto_20180821_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objective',
            name='time_completed',
            field=models.DecimalField(max_digits=4, decimal_places=1, null=True),
        ),
    ]
