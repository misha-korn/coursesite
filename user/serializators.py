from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role")

    def validate_username(self, username):
        user = User.objects.filter(username=username)
        if user.exists():
            raise serializers.ValidationError("Username already exists")
        return username

    def validate_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role", "email"]
