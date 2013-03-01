from django.forms.models import ModelForm
from SwissChess.main.models import Game, Tournament, Tour, Player


class GameForm(ModelForm):
    class Meta:
        model = Game

class TournamentForm(ModelForm):
    class Meta:
        model = Tournament

class TourForm(ModelForm):
    class Meta:
        model = Tour

class PlayerForm(ModelForm):
    class Meta:
        model = Player