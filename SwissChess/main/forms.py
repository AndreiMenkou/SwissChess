from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
import django.forms as forms
from django.forms.models import modelformset_factory
from django.forms.widgets import TextInput
from SwissChess.main.models import Game, Tournament, Tour, Player


class GameForm(forms.ModelForm):
    class Meta:
        model = Game

    def clean(self):
        super(GameForm, self).clean()
        data = self.cleaned_data
        if data.get('black_player') == data.get('white_player'):
            raise ValidationError('Players in game must be distinct')

        return data


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'players']


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player


class PlayerToTournamentForm(forms.Form):
    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all())


GameFormSet = modelformset_factory(Game, extra=0, exclude=('black_player', 'white_player', 'tour'))