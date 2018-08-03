
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Category


class UserSerializer(serializers.HyperlinkedModelSerializer):
    posts = serializers.HyperlinkedRelatedField(many=True, view_name='blog:post-detail',read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'posts')

class PostSerializer(serializers.HyperlinkedModelSerializer):
    create_by = serializers.ReadOnlyField(source='create_by.username')

    class Meta:
        model = Post
        fields = ('title', 'content', 'create_date', 'create_by')

    def create(self, validated_data):
        """
        Create and return a new Post instance, given the validated data.
        """
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing Post instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance