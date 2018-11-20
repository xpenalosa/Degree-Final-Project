from project.application.models import Tournament, Player
from rest_framework import serializers

class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tournament
        fields = (
            'url',
            'name',
            'editable', 'deletion_date'
        )

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = (
            'url',
            'name',
            'points', 'wins', 'losses',
            'disqualified',
           'tournament'
        )
