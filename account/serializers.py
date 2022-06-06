from .models import User
from rest_framework import serializers


# 유저 Serializer
class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            name=validated_data['name'],
            password=validated_data['password'],
        )
        return user

    class Meta:
        model = User
        fields = ['nickname', 'email', 'name', 'password']


# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    like_posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['nickname', 'like_posts', 'like_comments', 'email', 'name']
