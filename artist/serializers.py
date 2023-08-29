from rest_framework import serializers
from .models import Artist,Music
from django.core.validators import MinValueValidator
from django.utils import timezone

def max_value_current_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(f'Maximum value should be {current_year}.')

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class ListArtistSerializer(serializers.Serializer):
    artist_id = serializers.IntegerField()
    artist_name = serializers.CharField()
    dob = serializers.DateTimeField()
    gender = serializers.CharField()
    address = serializers.CharField()
    first_release_year = serializers.IntegerField()
    number_of_albums_released = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    user = UserSerializer()

class MusicSerializer(serializers.Serializer):
    artist_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    album_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    genre = serializers.ChoiceField(choices=Music.GENRE_CHOICES, required=False, allow_null=True)


class ArtistMusicSerializer(serializers.Serializer):
    artist_id = serializers.IntegerField()
    artist_name = serializers.CharField()
    dob = serializers.DateTimeField()
    gender = serializers.CharField()
    address = serializers.CharField()
    first_release_year = serializers.IntegerField()
    number_of_albums_released = serializers.IntegerField()
    artist_created_at = serializers.DateTimeField()
    artist_updated_at = serializers.DateTimeField()

class ListMusicSerializer(serializers.Serializer):
    music_id = serializers.IntegerField()  # Correct mapping to the column name from your query
    title = serializers.CharField()
    album_name = serializers.CharField()
    genre = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    artist = ArtistMusicSerializer(source='*')  # Use '*' to include all fields in the nested serializer

class UpdateMusicSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    album_name = serializers.CharField(required=False)
    genre = serializers.CharField(required=False)

class ArtistImportSerializer(serializers.Serializer):
    UserID = serializers.IntegerField()
    Name = serializers.CharField()
    DOB = serializers.DateTimeField()
    Gender = serializers.ChoiceField(choices=Artist.GENDERS)
    Address = serializers.CharField()
    FirstReleaseYear = serializers.IntegerField()
    NumberofAlbumsReleased = serializers.IntegerField()


