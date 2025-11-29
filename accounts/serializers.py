from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "confirm_password", "role")

    def validate(self, data):
        password = data.get("password")
        confirm = data.get("confirm_password")
        if password != confirm:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match! Try again"})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password") 
        user = CustomUser.objects.create_user(**validated_data)
        return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "first_name", "last_name", "role")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)