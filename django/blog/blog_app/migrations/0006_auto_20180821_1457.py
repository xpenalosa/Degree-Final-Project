# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0005_auto_20180821_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objective',
            name='priority',
            field=models.PositiveSmallIntegerField(default=3, choices=[(5, 'Critica'), (4, 'Alta'), (3, 'Normal'), (2, 'Baixa'), (1, 'Opcional')]),
        ),
    ]
