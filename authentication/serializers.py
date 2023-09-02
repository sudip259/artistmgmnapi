from rest_framework import serializers
from .models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)

class CreateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=500)
    role_type = serializers.ChoiceField(choices=CustomUser.ROLES)
    phone = serializers.CharField(max_length=20, allow_blank=True, allow_null=True)
    gender = serializers.ChoiceField(choices=CustomUser.GENDERS, allow_blank=True, allow_null=True)
    address = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
    dob = serializers.DateTimeField(allow_null=True)

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        hashed_password = make_password(raw_password)
        validated_data['password'] = hashed_password
        return CustomUser.objects.create(**validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class ListUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    role_type = serializers.CharField(max_length=14)
    email = serializers.EmailField(max_length=255)
    phone = serializers.CharField(max_length=20)
    gender = serializers.CharField(max_length=1)
    address = serializers.CharField(max_length=255)
    dob = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name','email', 'last_name', 'role_type', 'phone', 'gender', 'address', 'dob', 'created_at', 'updated_at', 'is_active']