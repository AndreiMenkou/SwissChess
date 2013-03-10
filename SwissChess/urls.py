from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from SwissChess.main.models import Player

admin.autodiscover()

urlpatterns = patterns('SwissChess.main.views',
    # Examples:
    url(r'^$', 'index'),
    url(r'^add/player$', 'add_player'),
    url(r'^add/tournament$', 'add_tournament'),
    url(r'^tournaments/(\d+)/$', 'tournament_details'),
    url(r'^tournaments/(\d+)/participants$', 'tournament_participants'),
    url(r'^tournaments/(\d+)/add/player$', 'add_players_to_tournament'),
    url(r'^tournaments/(\d+)/create$', 'create_tournament'),
    url(r'^tournaments/(\d+)/create/tour$', 'create_tour', name='create_tour'),
    url(r'^tournaments/edit/tour/(\d+)$', 'edit_tour'),
    url(r'^players$', 'players'),

    # url(r'^SwissChess/', include('SwissChess.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                            url(r'^static/(?P<path>.*)$', 'serve'),
                            )