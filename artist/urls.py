# app level api routing
from artist.views import create_artist,list_artist,update_artist,delete_artist,create_music,list_music,update_music,delete_music,export_artists_csv,import_artists_csv
from django.urls import path
urlpatterns = [
    path('api/artist/create', create_artist, name='create-artist'),
    path('api/artist/list', list_artist, name='list-artist'),
    path('api/update-artist/<int:artist_id>',update_artist, name='update-artist'),
    path('api/delete-artist/<int:artist_id>', delete_artist, name='delete-artist'),

    path('api/music/create', create_music, name='create-music'),
    path('api/music/list', list_music, name='list-music'),
    path('api/update-music/<int:music_id>',update_music, name='update-music'),
    path('api/delete-music/<int:music_id>', delete_music, name='delete-music'),
    path('api/artist/export-csv', export_artists_csv, name='export-artists-csv'),
    path('api/artist/import-csv', import_artists_csv, name='import-artists-csv'),
]