# Third party import
from rest_framework import serializers
from django.contrib.auth.models import User


# App level import
from .models import (
    Article, Comment, Notification
)
from .utils import get_markup_text


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class ArticlePOSTSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('id', 'title', 'body')

    def create(self, validated_data):
        try:
            raw_body = validated_data.get('body')
            article_body = get_markup_text(raw_body)
            validated_data['body'] = article_body
        except:
            pass

        article_instance = super(ArticlePOSTSerializer, self).create(
            validated_data)
        return article_instance


class ArticleGETSerializer(serializers.ModelSerializer):
    likers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'body', 'media_url',
                  'likers', 'contain_media')


class CommentPOSTSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('comment_body', 'article_id', 'user_username')

    def create(self, validated_data):
        try:
            raw_body = validated_data.get('comment_body')
            comment_body = get_markup_text(raw_body)
            validated_data['comment_body'] = comment_body
        except:
            pass

        comment_instance = super(CommentPOSTSerializer, self).create(
            validated_data)
        return comment_instance


class CommentGETSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'comment_body', 'user_username', 'article_id')


class NotificationGETSerializer(serializers.ModelSerializer):
    article_instance = ArticleGETSerializer(read_only=True)
    engager_name = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'notification_type',
                  'article_instance', 'engager_name')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
