# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from SwissChess.main.forms import GameForm, TournamentForm, TourForm, PlayerForm


def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

@login_required()
def add_game(request):
    return _add_model_instance(request, GameForm)

@login_required()
def add_tournament(request):
    return _add_model_instance(request, TournamentForm)

@login_required()
def add_tour(request):
    return _add_model_instance(request, TourForm)

@login_required()
def add_player(request):
    return _add_model_instance(request, PlayerForm)

def _add_model_instance(request, FormClass):
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            # process data
            return redirect(index)
    else:
        form = FormClass()

    return render(request, 'add.html', {'form': form, })