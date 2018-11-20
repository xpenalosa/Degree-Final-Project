# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here

class Tournament(models.Model):
    name = models.CharField(max_length=32)
    password = models.CharField(max_length=26)
    editable = models.BooleanField(default=True)
    deletion_date = models.DateField()


class Player(models.Model):
    name = models.CharField(max_length=16)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    disqualified = models.BooleanField(default=False)
    tournament = models.ForeignKey('Tournament',on_delete=models.CASCADE)
