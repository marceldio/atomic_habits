from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "phone",
            "tg_name",
            "chat_id",
            "country",
            "avatar",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            phone=validated_data.get("phone", ""),
            tg_name=validated_data.get("tg_name", ""),  # Telegram имя
            chat_id=validated_data.get("chat_id", ""),  # Telegram chat id
            country=validated_data.get("country", ""),
            avatar=validated_data.get("avatar", None),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Указываем email как поле для аутентификации"""

    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        """Добавляем email в токен"""
        token["email"] = user.email
        return token

    def validate(self, attrs):
        """Переносим логику извлечения email и пароля"""
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                "Email и пароль обязательны для заполнения."
            )

        try:
            """Ищем пользователя по email"""
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email не найден."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неправильный пароль."})

        """Передаем данные дальше для создания токена
            Передаем email как username"""
        attrs["username"] = user.email
        return super().validate(attrs)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        """Поля, которые можно редактировать"""
        fields = [
            "email",
            "phone",
            "tg_name",
            "chat_id",
            "country",
            "avatar",
        ]
