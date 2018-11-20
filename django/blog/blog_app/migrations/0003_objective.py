# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0002_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Objective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=80)),
                ('priority', models.PositiveSmallIntegerField(choices=[(5, 'Critical'), (4, 'High'), (3, 'Normal'), (2, 'Low'), (1, 'Optional')], default=3)),
                ('completed', models.BooleanField(default=False)),
                ('time_estimated', models.DecimalField(max_digits=4, decimal_places=1)),
                ('time_completed', models.DecimalField(max_digits=4, decimal_places=1)),
            ],
            options={
                'ordering': ('-priority', 'completed'),
            },
        ),
    ]
