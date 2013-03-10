from django.db import models
from django.db.models.query_utils import Q
from SwissChess.main.swiss import calc_new_elo_rating, get_numbser_of_tours

BLACK_COLOR = 'black'
WHITE_COLOR = 'white'


class Player(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    rating = models.IntegerField(min_value=1, max_value=3000, help_text='ELO rating, must be positive integer < 3000')

    class Meta:
        ordering = ('first_name', 'last_name')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_points_in_tournament(self, tournament):
        result = 0
        for tour in tournament.tour_set.all():
            games_black = tour.game_set.filter(black_player=self)[:1]
            if games_black.exists():
                game_result = games_black[0].result
                if game_result == u'BW':
                    result += 1.0
                elif game_result == u'WW':
                    result += 0.0
                else:
                    result += 0.5
                continue
            games_white = tour.game_set.filter(white_player=self)[:1]
            if games_white.exists():
                game_result = games_white[0].result
                if game_result == u'BW':
                    result += 0.0
                elif game_result == u'WW':
                    result += 1.0
                else:
                    result += 0.5

        return result


class Tournament(models.Model):
    name = models.CharField(max_length=30)
    players = models.ManyToManyField(Player, through='Membership', blank=True, null=True)
    created = models.BooleanField()
    progress = models.FloatField()

    def __unicode__(self):
        return 'Tournament ' + self.name

    def calc_progress(self):
        full_tours_needed = get_numbser_of_tours(self.players.count())
        full_games_needed = full_tours_needed * self.players.count() / 2
        played_games = 0
        for tour in self.tour_set.all():
            played_games += Game.objects.filter(tour=tour).exclude(result__isnull=True).count()

        return played_games * 100.0 / full_games_needed

    @property
    def is_finished(self):
        return self.progress == 100.0

    def update_progress(self):
        self.progress = self.calc_progress()
        self.save()

    @property
    def last_tour(self):
        tours = self.tour_set.all().order_by('-number')
        if tours:
            return tours[0]

    def played(self, player1, player2):
        for tour in self.tour_set.all():
            if tour.game_set.filter(Q(black_player=player1) | Q(black_player=player2),
                                    Q(white_player=player1) | Q(white_player=player2)):
                return True
            return False

    @property
    def results(self):
        memberships = [membership for membership in self.membership_set.all()]
        memberships.sort(cmp=lambda x, y: cmp(x.points, y.points)
            if abs(x.points - y.points) > 0.1 else cmp(x.buchholz_coeff, y.buchholz_coeff), reverse=True)
        players = []
        for membership in memberships:
            player = membership.player
            player.points = membership.points
            players.append(player)

        return players


class Membership(models.Model):
    player = models.ForeignKey(Player)
    tournament = models.ForeignKey(Tournament)
    points = models.FloatField()

    @property
    def buchholz_coeff(self):
        coeff = 0.0
        for tour in self.tournament.tour_set.all():
            game = tour.game_set.filter(Q(black_player=self.player) | Q(white_player=self.player)).get()
            if game.black_player == self.player:
                opponent = game.white_player
            else:
                opponent = game.black_player

            coeff += Membership.objects.filter(tournament=self.tournament).filter(player=opponent).get().points

        return coeff


class Tour(models.Model):
    number = models.IntegerField()
    tournament = models.ForeignKey(Tournament)
    finished = models.BooleanField()

    class Meta:
        ordering = ('number',)
        unique_together = ('number', 'tournament')

    def __unicode__(self):
        return 'Tour ' + str(self.number) + ' of ' + self.tournament.name

    @property
    def finished(self):
        return self.game_set.filter(result__isnull=True).count() == 0

    def get_player_color(self, player):
        game = self.game_set.filter(Q(black_player=player) | Q(white_player=player)).get()
        return BLACK_COLOR if game.black_player == player else WHITE_COLOR


class Game(models.Model):
    GAME_RESULT_TYPES = (
        ('BW', 'Black player win'),
        ('WW', 'White player win'),
        ('T', 'Tie'),
    )
    black_player = models.ForeignKey(Player, related_name='black player')
    white_player = models.ForeignKey(Player, related_name='white player')
    tour = models.ForeignKey(Tour)
    result = models.CharField(max_length=2, choices=GAME_RESULT_TYPES, blank=True, null=True)

    def __unicode__(self):
        return 'Game between %s and %s with result %s in %s' % \
               (self.black_player, self.white_player, self.result, self.tour)

    @property
    def winner(self):
        if self.result == 'BW':
            return self.black_player.id
        elif self.result == 'WW':
            return self.white_player.id
        elif self.result == 'T':
            return -1
        else:
            return 0

    def save(self, *args, **kwargs):
        if self.black_player == self.white_player:
            raise ValueError('Players in game must be distinct')
        super(Game, self).save(*args, **kwargs)
        if self.result:
            if self.result == Game.GAME_RESULT_TYPES[0][0]:  # black player win
                self._add_points_to_player(self.black_player, 1.0)
                Game._update_players_rating(self.white_player, self.black_player, 0.0)
            elif self.result == Game.GAME_RESULT_TYPES[1][0]:  # white player win
                self._add_points_to_player(self.white_player, 1.0)
                Game._update_players_rating(self.white_player, self.black_player, 1.0)
            elif self.result == Game.GAME_RESULT_TYPES[2][0]:  # tie
                self._add_points_to_player(self.white_player, 0.5)
                self._add_points_to_player(self.black_player, 0.5)
                Game._update_players_rating(self.white_player, self.black_player, 0.5)

    def _add_points_to_player(self, player, points):
        membership = Membership.objects.filter(tournament=self.tour.tournament).filter(player=player).get()
        membership.points += points
        membership.save()

    @staticmethod
    def _update_players_rating(player1, player2, result):
        player1.rating = calc_new_elo_rating(player1.rating, player2.rating, result)
        player1.save()
        player2.rating = calc_new_elo_rating(player2.rating, player1.rating, 1.0 - result)
        player2.save()