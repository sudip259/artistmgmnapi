from rest_framework import status
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from .serializers import LoginSerializer,CreateUserSerializer,UpdateUserSerializer,ListUserSerializer
from django.contrib.auth.hashers import check_password
from django.db import connection
from utilities.role_checker import role_required
from authentication.models import CustomUser
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# login view
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        query = "SELECT * FROM custom_user WHERE email = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [email])
            user_row = cursor.fetchone()

        if user_row and check_password(password, user_row[4]):
            user_id = user_row[0]

            # Fetch the user instance using your CustomUser model
            user_instance = CustomUser.objects.get(id=user_id)

            token, created = Token.objects.get_or_create(user=user_instance)

            user_details = {
                'id': user_row[0],
                'email': user_row[2],
                'first_name': user_row[1],
                'role':user_row[5],
                'token': token.key
            }

            return Response(user_details, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# create user creation view
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['super_admin'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        raw_password = data['password']
        hashed_password = make_password(raw_password)

        query = """
            INSERT INTO custom_user (first_name, last_name, email, password, role_type, phone, gender, address, dob, created_at, updated_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['first_name'], data['last_name'], data['email'], hashed_password, data['role_type'],
            data['phone'], data['gender'], data['address'], data['dob'],
            timezone.now(), timezone.now(), True
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
        except IntegrityError:
            return Response({'message': 'Email address already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the newly created user's token
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            return Response({'message': 'Failed to create user'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)

        user_details = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'token': token.key
        }

        return Response(user_details, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# getall users
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['super_admin'])
def list_users(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, first_name, last_name, email, role_type, phone, gender, address, dob, created_at, updated_at, is_active FROM custom_user")
            data = cursor.fetchall()

        user_list = []
        

        for row in data:
            print("row[0]++++++++++",row[0])
            user_dict = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'role_type': row[4],
                'phone': row[5],
                'gender': row[6],
                'address': row[7],
                'dob': row[8],
                'created_at': row[9],
                'updated_at': row[10],
                'is_active': row[11],
            }
            user_list.append(user_dict)

        serializer = ListUserSerializer(data=user_list, many=True)
        serializer.is_valid()  # Check validation (optional)

        return Response(serializer.data, status=status.HTTP_200_OK)


# update user
@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['super_admin'])
def partial_update_user(request, user_id):
    if request.method == 'PATCH':
        data = request.data

        serializer = UpdateUserSerializer(data=data,partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fields_to_update = []
        values = []

        for field, value in serializer.validated_data.items():
            fields_to_update.append(f'{field}=%s')
            values.append(value)

        values.append(user_id)  # Adding user_id as the last value

        # Check for email uniqueness if the email is being updated
        new_email = data.get('email')
        if new_email:
            existing_user_with_email = CustomUser.objects.exclude(id=user_id).filter(email=new_email).first()
            if existing_user_with_email:
                return Response({'message': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        update_query = f"""
            UPDATE custom_user
            SET {', '.join(fields_to_update)}, updated_at=NOW()
            WHERE id=%s
        """

        with connection.cursor() as cursor:
            cursor.execute(update_query, values)

        return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)

# delete user
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required(['super_admin'])
def delete_user(request, user_id):
    if request.method == 'DELETE':
        # Delete tokens associated with the user
        delete_tokens_query = """
            DELETE FROM authtoken_token
            WHERE user_id = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(delete_tokens_query, [user_id])

        # Delete music records associated with the user's artist
        delete_music_query = """
            DELETE FROM music
            WHERE artist_id IN (
                SELECT id
                FROM artist
                WHERE user_id = %s
            )
        """

        with connection.cursor() as cursor:
            cursor.execute(delete_music_query, [user_id])

        # Delete artist records associated with the user
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM artist WHERE user_id = %s", [user_id])

        # Now, delete the user
        delete_user_query = """
            DELETE FROM custom_user
            WHERE id = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(delete_user_query, [user_id])

        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    if request.method == 'POST':
        try:
            token = Token.objects.get(user=request.user)
            token.delete()  # Delete the token associated with the user
            
            # Clear the session manually
            request.session.flush()
            
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'message': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)





















