from django.contrib import admin
from SwissChess.main.models import Player, Tournament, Tour, Game, Membership

admin.site.register(Player)
admin.site.register(Tournament)
admin.site.register(Tour)
admin.site.register(Game)
admin.site.register(Membership)