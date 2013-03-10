# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from SwissChess.main.forms import TournamentForm, PlayerForm, PlayerToTournamentForm, GameFormSet
from SwissChess.main.models import Tournament, Player, Membership, Tour
from SwissChess.main.swiss import populate_tour_games

ITEMS_PER_PAGE = 20


def index(request):
    return render(request, 'index.html', {
        'tournaments': _get_paginated_objects(request, Tournament.objects.all().order_by('-id'))
    })


@login_required()
def add_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = Tournament(name=form.cleaned_data.get('name'), progress=0.0, created=False)
            tournament.save()
            for player in form.cleaned_data.get('players'):
                membership = Membership(tournament=tournament, player=player, points=0.0)
                membership.save()
            return redirect(index)
    else:
        form = TournamentForm()

    return render(request, 'add.html', {
        'form': form
    })


@login_required()
@transaction.commit_on_success
def create_tour(request, tournament_id):
    tournament = Tournament.objects.get(pk=tournament_id)
    created_tours = Tour.objects.filter(tournament=tournament).count()
    tour = Tour.objects.create(number=created_tours + 1, tournament=tournament)
    populate_tour_games(tournament, tour)
    return redirect(tournament_details, tournament_id)


@login_required()
def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(players)
    else:
        form = PlayerForm()

    return render(request, 'add.html', {
        'form': form
    })


def tournament_details(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    players = tournament.results
    tours = tournament.tour_set.all()
    tour = None
    games = []
    if tours:
        tour_num = request.GET.get('tour', None)
        if tour_num:
            tour = get_object_or_404(tours, number=tour_num)
        else:
            tour = tours.order_by('-number')[0]
        games = tour.game_set.all()

    return render(request, 'tournament_details.html', {
        'tournament': tournament,
        'players': players,
        'tours': tours,
        'tour': tour,
        'games': games
    })


@login_required()
@transaction.commit_on_success
def edit_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)

    if request.method == 'POST':
        games_formset = GameFormSet(request.POST, queryset=tour.game_set.filter(result__isnull=True))
        if games_formset.is_valid():
            games_formset.save()
            tour.tournament.update_progress()
            return redirect(tournament_details, tour.tournament.id)
    else:
        games_formset = GameFormSet(queryset=tour.game_set.filter(result__isnull=True))

    return render(request, 'edit_tour.html', {
        'tour': tour,
        'games_formset': games_formset
    })


def add_players_to_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)

    if request.method == 'POST':
        form = PlayerToTournamentForm(request.POST, tournament_id)
        if form.is_valid():
            for player in form.cleaned_data.get('players'):
                Membership.objects.create(player=player, tournament=tournament, points=0.0)
            return redirect(tournament_details, tournament_id)
    else:
        form = PlayerToTournamentForm()
        form.fields['players'].queryset = Player.objects.all().exclude(membership__tournament=tournament)

    return render(request, 'add.html', {
        'form': form
    })


@login_required()
def create_tournament(request, tournament_id):
    Tournament.objects.filter(pk=tournament_id).update(created=True)
    return redirect(tournament_details, tournament_id)


def players(request):
    return render(request, 'players.html', {
        'players': _get_paginated_objects(request, Player.objects.all().order_by('-rating'))
    })


def _get_paginated_objects(request, objects):
    paginator = Paginator(objects, ITEMS_PER_PAGE)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        paginated_objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_objects = paginator.page(paginator.num_pages)

    return paginated_objects


def tournament_participants(request, tournament_id):
    tournament = Tournament.objects.get(pk=tournament_id)

    return render(request, 'participants.html', {
        'tournament': tournament,
        'players': tournament.results
    })