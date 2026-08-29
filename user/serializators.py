from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from itsdangerous import BadSignature, SignatureExpired
from rest_framework import serializers, permissions

from user.tokens import read_reset_password_token, make_change_email_token, read_change_email_token, \
    read_verify_email_token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role")

    def validate_username(self, username):
        user = User.objects.filter(username=username)
        if user.exists():
            raise serializers.ValidationError("Имя занято")
        return username

    def validate_email(self, email):
        user = User.objects.filter(email=email)
        if user.exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован")
        return email

    def validate_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role", "email", "email_verified", "image"]
        read_only_fields = [
            "id",
            "username",
            "role",
            "email",
            "email_verified",
        ]


class PublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role", "image"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Текущий пароль неверный")
        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.context["request"].user)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            payload = read_reset_password_token(data["token"])
        except SignatureExpired:
            raise serializers.ValidationError("Срок действия токена истек") from None
        except BadSignature:
            raise serializers.ValidationError("Ссылка не действительна") from None

        user = User.objects.filter(pk=payload.get("uid"), is_active=True).first()

        if user is None:
            raise serializers.ValidationError("Ссылка не действительна")

        if payload.get("pwd") != user.password[:16]:
            raise serializers.ValidationError("Ссылка уже использована")

        validate_password(data["new_password"], user=user)

        self.user = user

        return data

    def save(self, **kwargs):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user


class EmailChangeRequestSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    new_email = serializers.EmailField()

    def validate_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Текущий пароль неверный")
        return value

    def validate_new_email(self, value):
        if self.context['request'].user.email == value:
            raise serializers.ValidationError("Это ваш текущий адрес")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован")
        return value

class EmailChangeConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        try:
            payload = read_change_email_token(data["token"])
        except SignatureExpired:
            raise serializers.ValidationError("Срок действия токена истек") from None
        except BadSignature:
            raise serializers.ValidationError("Ссылка не действительна") from None

        user = User.objects.filter(pk=payload.get("uid"), is_active=True).first()

        new_email = payload.get("new_email")

        if user is None:
            raise serializers.ValidationError("Ссылка не действительна")

        if payload.get("pwd") != user.password[:16]:
            raise serializers.ValidationError("Ссылка не действительна")

        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован")

        self.user = user
        self.new_email = new_email

        return data

    def save(self, **kwargs):
        self.user.email = self.new_email
        self.user.email_verified = True
        self.user.save(update_fields=["email", "email_verified"])
        return self.user

class VerifyEmailConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        try:
            payload = read_verify_email_token(token=data["token"])
        except SignatureExpired:
            raise serializers.ValidationError("Срок действия токена истек") from None
        except BadSignature:
            raise serializers.ValidationError("Ссылка не действительна") from None

        user = User.objects.filter(pk=payload.get("uid"), is_active=True).first()

        if user is None:
            raise serializers.ValidationError("Ссылка не действительна")

        if payload.get("pwd") != user.password[:16]:
            raise serializers.ValidationError("Ссылка не действительна")

        if user.email_verified:
            raise serializers.ValidationError("Ваш email уже подтвержден")

        self.user = user

        return data

    def save(self, **kwargs):
        self.user.email_verified = True
        self.user.save(update_fields=["email_verified"])
        return self.user