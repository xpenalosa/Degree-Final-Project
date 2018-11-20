# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import viewsets

from project.application.models import Tournament, Player
from project.application.serializers import TournamentSerializer, PlayerSerializer

# Create your views here.

class TournamentViewSet(viewsets.ModelViewSet):
    """API endpoint for tournaments."""
    queryset = Tournament.objects.all().order_by('id')
    serializer_class = TournamentSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """API endpoint for players."""
    # Filter to a certain tournament?
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
