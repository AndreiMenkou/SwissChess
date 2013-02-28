from django.db import models

# Create your models here.

class Player(models.Model):
    rating = models.IntegerField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    class Meta:
        ordering = ('first_name', 'last_name')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Tournament(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return 'Tournament ' + self.name

class Tour(models.Model):
    number = models.IntegerField()
    tournament = models.ForeignKey(Tournament)

    class Meta:
        ordering = ('number',)
        unique_together = ('number', 'tournament')

    def __unicode__(self):
        return 'Tour ' + str(self.number) + ' of ' + self.tournament.name

class Game(models.Model):
    black_player = models.ForeignKey(Player, related_name='black player')
    white_player = models.ForeignKey(Player, related_name='white player')
    # tournament = models.ForeignKey(Tournament)
    tour = models.ForeignKey(Tour)
    result = models.IntegerField()

    def __unicode__(self):
        return 'Game between %s and %s with result %s in %s' %\
               (self.black_player, self.white_player, self.result, self.tour)