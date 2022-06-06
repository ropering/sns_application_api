from rest_framework import serializers

from feed.models import Feed, Comment


# Feed Serializer
class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['id', 'title', 'created_at', 'updated_at', 'user', 'content', 'like_count']


# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')

    class Meta:
        model = Comment
        fields = ['id', 'feed', 'like_count', 'created_at', 'user', 'comment']
