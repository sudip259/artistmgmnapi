from django.db import connection,transaction
import csv
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Artist, CustomUser,Music
from .serializers import ArtistSerializer,ListArtistSerializer,MusicSerializer,ListMusicSerializer,UpdateMusicSerializer,ArtistImportSerializer
import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from utilities.role_checker import role_required
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse

# artist create
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist_manager'])
def create_artist(request):
    data = request.data

    user_id = data.get('user_id')  # Assuming user_id is sent in the request data

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user already has an associated artist
    if hasattr(user, 'artist'):
        return Response({'message': 'User already has an associated artist'}, status=status.HTTP_400_BAD_REQUEST)

    # Artist data
    artist_data = {
        'user_id': user_id,
        'name': data.get('name'),
        'dob': data.get('dob'),
        'gender': data.get('gender'),
        'address': data.get('address'),
        'first_release_year': data.get('first_release_year'),
        'number_of_albums_released': data.get('number_of_albums_released'),
    }

    # Serialize artist data
    artist_serializer = ArtistSerializer(data=artist_data)
    if artist_serializer.is_valid():
        artist_serializer.save()
        return Response({'message': 'Artist created successfully', 'artist': artist_serializer.data}, status=status.HTTP_201_CREATED)
    return Response(artist_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# artist list
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['super_admin','artist_manager','artist'])
def list_artist(request):
    query = """
        SELECT
            a.id AS artist_id,
            u.id AS user_id,
            u.first_name, u.last_name,
            a.name AS artist_name, a.dob, a.gender, a.address,
            a.first_release_year, a.number_of_albums_released,
            a.created_at, a.updated_at
        FROM artist AS a
        INNER JOIN custom_user AS u ON a.user_id = u.id
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    keys = [
        "artist_id", "user_id", "first_name", "last_name",  # Update here
        "artist_name", "dob", "gender", "address",
        "first_release_year", "number_of_albums_released",
        "created_at", "updated_at"
    ]
    results_dicts = [dict(zip(keys, row)) for row in results]

    for artist_dict in results_dicts:
        artist_dict['user'] = {
            'id': artist_dict.pop('user_id'),
            'first_name': artist_dict.pop('first_name'),
            'last_name': artist_dict.pop('last_name'),
        }

    serializer = ListArtistSerializer(results_dicts, many=True)
    return Response(serializer.data)


# update artist
@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist_manager'])
def update_artist(request, artist_id):
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        return Response({'message': 'Artist not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    user_id = data.get('user_id')

    # Check if a user with the same user_id already exists
    if Artist.objects.filter(user_id=user_id).exclude(id=artist_id).exists():
        return Response({'message': 'User is already associated with this user id'}, status=status.HTTP_400_BAD_REQUEST)

    query = """
        UPDATE artist
        SET name = %s, dob = %s, gender = %s, address = %s, user_id = %s,
            first_release_year = %s, number_of_albums_released = %s, updated_at = %s
        WHERE id = %s
    """

    values = (
        data.get('name'), data.get('dob'), data.get('gender'), data.get('address'), user_id,
        data.get('first_release_year'), data.get('number_of_albums_released'),
        timezone.now(), artist_id
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    return Response({'message': 'Artist updated successfully'})

# delete artist
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist_manager'])
def delete_artist(request, artist_id):
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        return JsonResponse({'message': 'Artist not found'}, status=404)

    with connection.cursor() as cursor:
        # Delete related Music instances
        cursor.execute("DELETE FROM music WHERE artist_id = %s", [artist_id])

        # Delete the Artist instance
        cursor.execute("DELETE FROM artist WHERE id = %s", [artist_id])

    return JsonResponse({'message': 'Artist deleted successfully'})

# create music
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist'])
def create_music(request):
    serializer = MusicSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        artist_id = data['artist_id']
        title = data['title']
        album_name = data.get('album_name')
        genre = data.get('genre')

        query = """
            INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            artist_id, title, album_name, genre,
            timezone.now(), timezone.now()
        )

        with connection.cursor() as cursor:
            cursor.execute(query, values)

        return Response({'message': 'Music created successfully'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# list music
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist','artist_manager','super_admin'])
def list_music(request):
    query = """
        SELECT
            m.id AS music_id,
            m.title, m.album_name, m.genre,
            m.created_at, m.updated_at,
            a.id AS artist_id, a.name AS artist_name, a.dob, a.gender, a.address,
            a.first_release_year, a.number_of_albums_released, a.created_at AS artist_created_at, a.updated_at AS artist_updated_at
        FROM music AS m
        INNER JOIN artist AS a ON m.artist_id = a.id
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    keys = [
        "music_id", "title", "album_name", "genre",
        "created_at", "updated_at",
        "artist_id", "artist_name", "dob", "gender", "address",
        "first_release_year", "number_of_albums_released", "artist_created_at", "artist_updated_at"
    ]
    results_dicts = [dict(zip(keys, row)) for row in results]

    serializer = ListMusicSerializer(results_dicts, many=True)
    return Response(serializer.data)

# update music
@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist'])
def update_music(request, music_id):
    try:
        music = Music.objects.get(id=music_id)
    except Music.DoesNotExist:
        return Response({'message': 'Music not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateMusicSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        

        query = """
            UPDATE music
            SET title = %s, album_name = %s, genre = %s, updated_at = %s, artist_id = %s, dob = %s,
            WHERE id = %s
        """

        values = (
            data.get('title', music.title),
            data.get('album_name', music.album_name),
            data.get('genre', music.genre),
            data.get('dob', music.dob),
            timezone.now(),
            data.get('artist_id', music.artist_id.id),  # Use artist_id from validated data
            music_id
        )

        with connection.cursor() as cursor:
            cursor.execute(query, values)

        return Response({'message': 'Music updated successfully'})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist'])
def delete_music(request, music_id):
    query = """
        DELETE FROM music WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [music_id])

    return Response({'message': 'Music deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# export artist in csv format
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist_manager'])
def export_artists_csv(request):
    query = """
        SELECT
            a.id, a.user_id,
            a.name,
            TO_CHAR(a.dob, 'YYYY-MM-DD') AS dob,
            CASE
                WHEN a.gender = 'm' THEN 'Male'
                WHEN a.gender = 'f' THEN 'Female'
                WHEN a.gender = 'o' THEN 'Other'
                ELSE ''
            END AS gender,
            a.address, a.first_release_year, a.number_of_albums_released,
            TO_CHAR(a.created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
            TO_CHAR(a.updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at
        FROM artist a
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        artists = cursor.fetchall()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="artists.csv"'

    csv_writer = csv.writer(response, quoting=csv.QUOTE_NONNUMERIC)
    csv_writer.writerow(['ID', 'UserID', 'Name', 'DOB', 'Gender', 'Address', 'FirstReleaseYear', 'NumberofAlbumsReleased', 'CreatedAt', 'UpdatedAt'])

    for artist in artists:
        csv_writer.writerow(artist)

    return response

# import artist
@csrf_protect
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['artist_manager'])
def import_artists_csv(request):
    csv_file = request.FILES.get('csv_file')

    if not csv_file:
        return JsonResponse({'error': 'No CSV file provided'}, status=400)

    try:
        decoded_file = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(decoded_file.splitlines())

        existing_user_ids = set(CustomUser.objects.values_list('id', flat=True))
        imported_user_ids = set(Artist.objects.values_list('user_id__id', flat=True))  
        errors = []

        with connection.cursor() as cursor:
            for row in csv_reader:
                user_id = row.get('UserID')
                if not user_id.isdigit() or int(user_id) not in existing_user_ids:
                    errors.append({'UserID': 'Invalid or non-existent UserID'})
                    continue

                if int(user_id) in imported_user_ids:
                    print('duplicate user')
                    errors.append({'UserID': 'Duplicate UserID '+str(user_id)})
                    continue

                imported_user_ids.add(user_id)

                try:
                    dob = row.get('DOB')
                    print(dob)
                except ValueError:
                    errors.append({'DOB': 'Invalid date format'})

                gender = row.get('Gender')
                if gender not in dict(Artist.GENDERS).keys():
                    errors.append({'Gender': 'Invalid gender value'})

                try:
                    first_release_year = int(row.get('FirstReleaseYear'))
                    if first_release_year < 1984 or first_release_year > datetime.datetime.now().year:
                        errors.append({'FirstReleaseYear': 'Invalid year value'})
                except (ValueError, TypeError):
                    errors.append({'FirstReleaseYear': 'Invalid year value'})

                try:
                    num_albums = int(row.get('NumberofAlbumsReleased'))
                except (ValueError, TypeError):
                    num_albums = None

                try:
                    created_at = timezone.now()
                except ValueError:
                    created_at = None

                try:
                    updated_at = timezone.now()
                except ValueError:
                    updated_at = None

                if errors:
                    continue

                try:
                    artist = Artist(
                        user_id_id=user_id,
                        name=row.get('Name'),
                        dob=dob,
                        gender=gender,
                        address=row.get('Address'),
                        first_release_year=first_release_year,
                        number_of_albums_released=num_albums,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    artist.full_clean()  # Run model validation
                    artist.save()
                except ValidationError as e:
                    errors.append(e.message_dict)

            if errors:
                return JsonResponse({'errors': errors}, status=400)

            return JsonResponse({'message': 'Artists imported successfully'}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)