
from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from authentication.models import CustomUser

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)

class Artist(models.Model):
    GENDERS = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other'),
    )
    user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='artist',blank=False,null=False,db_column='user_id')
    name = models.CharField(max_length=255, blank=False, null=False)
    dob = models.DateTimeField(blank=True, null=True)
    gender = models.CharField(choices=GENDERS,blank=True, null=True,max_length=1)
    address = models.CharField(max_length=255,blank=True, null=True)
    first_release_year = models.PositiveIntegerField(
        default=current_year(), validators=[MinValueValidator(1984), max_value_current_year],blank=True,null=True)
    number_of_albums_released = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'artist'


class Music(models.Model):
    GENRE_CHOICES = (
        ('rnb', 'R&B'),
        ('country', 'Country'),
        ('classic', 'Classic'),
        ('rock', 'Rock'),
        ('jazz', 'Jazz'),
    )
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE,related_name='music',blank=False,null=False,db_column='artist_id')
    title = models.CharField(max_length=255, blank=False, null=False)
    album_name = models.CharField(max_length=255, blank=True, null=True)
    genre = models.CharField(choices=GENRE_CHOICES,blank=True,null=True,max_length=14)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'music'  