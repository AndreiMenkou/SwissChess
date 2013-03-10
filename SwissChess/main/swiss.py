PRIZES_NUMBER = 3


def get_numbser_of_tours(player_number):
    """
    Calculates number of tours needed for play Tournament
    with passed number of players
    """
    from math import log

    return int(round(log(player_number, 2) + log(PRIZES_NUMBER, 2)))


def calc_new_elo_rating(rating, opponent_rating, game_result):
    expected_result = 1 / (1 + pow(10, (opponent_rating - rating) / 400.0))
    delta = get_elo_rating_coefficient(rating) * (game_result - expected_result)
    return rating + int(delta)


def get_elo_rating_coefficient(rating):
    """
    Return K-factor according to The United States Chess Federation (USCF)
    """
    if rating < 2100:
        return 32
    elif rating < 2400:
        return 24
    else:
        return 16


def populate_tour_games(tournament, tour):
    helper = SwissHelper(tournament, tour)
    helper.create_tour_games()


class SwissHelper(object):
    def __init__(self, tournament, tour):
        self.tournament = tournament
        self.tour = tour
        self.players = []
        self.players = [player for player in tournament.players.all()]
        for player in self.players:
            player.points = player.get_points_in_tournament(tournament)
        self.players.sort(cmp=lambda x, y: cmp(x.points, y.points)
            if abs(x.points - y.points) > 0.1 else cmp(x.rating, y.rating), reverse=True)

        # create matrix of played games for not to access every time to DB
        self.game_matrix = {}
        for player in self.players:
            self.game_matrix[player.id] = []
        for tour in tournament.tour_set.all():
            for game in tour.game_set.all():
                player1 = game.black_player
                player2 = game.white_player
                self.game_matrix[player1.id].append(player2.id)
                self.game_matrix[player2.id].append(player1.id)

    def _played(self, a_id, b_id):
        return self.game_matrix[a_id].count(b_id) > 0 and self.game_matrix[b_id].count(a_id) > 0

    def _get_next_tour_games(self):
        games = []
        free_players = [player.id for player in self.players]
        res = self._backtrack(free_players[0], games, free_players)
        if not res:
            raise RuntimeError('Error while creating next tour for %s' % self)
        return games

    # recursive algorithm for finding pair of players that
    # didn't play in this tournament yet
    def _backtrack(self, player, games, free_players):
        for opponent in free_players:
            if opponent != player and not self._played(player, opponent):
                games.append((player, opponent))
                free_players.remove(opponent)
                free_players.remove(player)
                if len(free_players) == 0:
                    return True
                res = self._backtrack(free_players[0], games, free_players)
                if res:
                    return True
                else:
                    free_players.append(opponent)
                    free_players.append(player)
                    games.remove((player, opponent))

    def create_tour_games(self):
        games = self._get_next_tour_games()
        for game in games:
            self._select_color(*game)

    def _select_color(self, a_id, b_id):
        from SwissChess.main.models import Game, Player, BLACK_COLOR

        player1 = Player.objects.get(pk=a_id)
        player2 = Player.objects.get(pk=b_id)
        # looking for colors in last 3 tours, '0' tour is just created - so empty
        tours = self.tournament.tour_set.all().order_by('-number')[1:4]
        if tours.count() == 0:  # there is not played tours and games in this tournament -> select random colors for players
            Game.objects.create(black_player=player1, white_player=player2, tour=self.tour)
        else:
            last_colors1 = [_tour.get_player_color(player1) for _tour in tours]
            print "Last colors of", player1, last_colors1
            last_colors2 = [_tour.get_player_color(player2) for _tour in tours]
            print "Last colors of", player2, last_colors2
            if last_colors1[0] != last_colors2[0]:  # last colors differ -> select different colors
                print 1
                if last_colors1[0] == BLACK_COLOR:
                    print 2
                    Game.objects.create(black_player=player2, white_player=player1, tour=self.tour)
                else:
                    print 3
                    Game.objects.create(black_player=player1, white_player=player2, tour=self.tour)
            else:
                print 4
                if last_colors1.count(BLACK_COLOR) > last_colors2.count(BLACK_COLOR):
                    print 5
                    Game.objects.create(black_player=player2, white_player=player1, tour=self.tour)
                else:
                    print 6
                    Game.objects.create(black_player=player1, white_player=player2, tour=self.tour)