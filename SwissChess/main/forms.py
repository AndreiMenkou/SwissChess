from django.core.exceptions import ValidationError
import django.forms as forms
from django.forms.models import modelformset_factory
from SwissChess.main.models import Game, Tournament, Tour, Player


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'players']


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0 or rating > 3000:
            raise ValidationError('Must be in range 0..3000')

        return rating


class PlayerToTournamentForm(forms.Form):
    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all())


GameFormSet = modelformset_factory(Game, extra=0, exclude=('black_player', 'white_player', 'tour'))