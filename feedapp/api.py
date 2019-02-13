# Core import
import os
import json
import asyncio
from collections import defaultdict

# Third party import
import websockets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.http import JsonResponse

from django.db.utils import IntegrityError

# App level import
from .serializers import (
    UserSerializer, ArticlePOSTSerializer, ArticleGETSerializer,
    CommentGETSerializer, CommentPOSTSerializer, NotificationGETSerializer
)
from .models import (
    Article, Comment, Notification
)
from .constants import (
    ERROR_MESSAGE, SUCCESS_MESSAGE
)
from src import settings


class ArticlePostAPI(APIView):

    def post(self, request, format=None):
        serilized_data = ArticlePOSTSerializer(data=request.data)

        if serilized_data.is_valid():
            article_instance = serilized_data.save()
            article_instance.written_by = request.user
            article_instance.save()
            response = {'article_id': article_instance.id}
            status_code = status.HTTP_201_CREATED

        else:
            response = serilized_data.errors
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(response, status=status_code)


class FeedGetAPI(APIView):

    def get(self, request, format=None):
        comment_dict = defaultdict(list)
        response, status_code = [], status.HTTP_200_OK

        articles_list = Article.objects.all()
        articles_list_ids = [article.id for article in articles_list]
        comment_list = Comment.objects.filter(article_id__in=articles_list_ids)

        serilized_article_list = ArticleGETSerializer(articles_list, many=True)
        serilized_comment_list = CommentGETSerializer(comment_list, many=True)

        for each_comment in serilized_comment_list.data:
            article_id = each_comment.get('article_id')
            comment_dict[article_id].append(each_comment)

        for each_article in serilized_article_list.data:
            id = each_article.get('id')
            each_article['comments'] = comment_dict.get(id)
            likers = [like.get('username')
                      for like in each_article.get('likers')]
            if request.user.username in likers:
                each_article['liked'] = True
            else:
                each_article['liked'] = False

            response.append(each_article)

        return Response(response, status=status_code)


class LikeAPIView(APIView):

    def post(self, request, format=None):
        article_id = request.data.get('id')

        try:
            article_instance = Article.objects.get(id=article_id)
            article_instance.likers.add(request.user)
            article_instance.save()

            Notification.objects.get_or_create(
                notification_type='Liked',
                user_instance=article_instance.written_by,
                article_instance=article_instance,
                engager_name=request.user
            )
            response = SUCCESS_MESSAGE.get('like')
            status_code = status.HTTP_200_OK

        except (IntegrityError, Article.DoesNotExist, TypeError) as e:
            response = ERROR_MESSAGE.get('like')
            status_code = status.HTTP_400_BAD_REQUEST
            print(e)

        return Response(response, status=status_code)


class CommentPostAPI(APIView):

    def post(self, request, format=None):
        request.data['user_username'] = request.user.username
        serilized_data = CommentPOSTSerializer(data=request.data)

        if serilized_data.is_valid():
            serilized_data.save()
            article_id = request.data.get('article_id')
            self.update_notification(article_id, request)
            response = SUCCESS_MESSAGE.get('comment')
            status_code = status.HTTP_201_CREATED

        else:
            response = serilized_data.errors
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(response, status=status_code)

    def update_notification(self, article_id, request):

        try:
            article_instance = Article.objects.get(id=article_id)
            Notification.objects.create(
                notification_type='Commented',
                user_instance=article_instance.written_by,
                article_instance=article_instance,
                engager_name=request.user
            )

        except (Article.DoesNotExist,) as e:
            print(e)


class NotificationGetAPI(APIView):

    def get(self, request, format=None):
        user = request.user
        notification_instances = Notification.objects.filter(
            user_instance=user)
        serilized_notification = NotificationGETSerializer(
            notification_instances, many=True)

        return Response(serilized_notification.data)


class AuthenticationAPI(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        response = {}
        status_code = status.HTTP_400_BAD_REQUEST

        data = request.data
        username = data.get('username')
        password = data.get('password')

        try:
            user_instance = User.objects.get(username=username)
            assert_password = user_instance.check_password(password)

            if assert_password:
                token_instance = Token.objects.get_or_create(
                    user=user_instance)[0]
                response['Authorization'] = 'Token ' + token_instance.key
                status_code = status.HTTP_200_OK

            else:
                response['error'] = 'Check your username or password.'

        except (User.DoesNotExist,) as e:
            response['error'] = 'Check your username or password.'
            print(e)

        return Response(response, status=status_code)


class RegistrationAPI(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        serilized_data = UserSerializer(data=request.data)

        if serilized_data.is_valid():
            serilized_data.save()
            response = SUCCESS_MESSAGE.get('user')
            status_code = status.HTTP_201_CREATED

        else:
            response = serilized_data.errors
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(response, status=status_code)


class SearchAPI(APIView):

    def get(self, request, query, type, format=None):
        text = query
        query_type = type

        if query_type == 'person':
            response = self.get_person_search(text)
        elif query_type == 'hashtag':
            response = self.get_hastag_search(text)
        else:
            response = self.get_title_search(text)

        return Response(response)

    def get_title_search(self, text):
        article_instances = Article.objects.filter(title__contains=text)
        result = ArticleGETSerializer(article_instances, many=True)
        return result.data

    def get_hastag_search(self, text):
        text = '#' + text
        try:
            article_instances = Article.objects.filter(body__contains=text)
            comment_instances = Comment.objects.filter(
                comment_body__contains=text)
            articles = ArticleGETSerializer(article_instances, many=True)
            comments = CommentGETSerializer(comment_instances, many=True)
            all_result = articles.data + comments.data
            all_result = sorted(
                all_result, key=lambda x: x.get('timestamp'), reverse=True)
        except:
            all_result = []

        return all_result

    def get_person_search(self, text):
        user_instances = User.objects.filter(username=text)
        result = [{'username': user.username} for user in user_instances]
        return result


def upload_file(request, id):
    """File upload controller."""

    if request.method == 'POST':
        try:
            article_instance = Article.objects.get(id=id)
            try:
                files = request.FILES.getlist('file')
                file_path = upload_handler(files)[0]
                article_instance.media_url = '/media/{}'.format(file_path)
                article_instance.save()
                context = {'message': 'Upload Succesfull'}
                asyncio.run(update_live_feed(article_instance, request))
                return JsonResponse({'message': 'File uploaded successfully.'})
            except:
                asyncio.run(update_live_feed(article_instance, request))
                context = {'message': 'Error Processing File.'}
                return JsonResponse(context)
        except:
            context = {'message': 'Failed to upload File.'}
            return JsonResponse(context)


def upload_handler(files):
    """Save the uploaded file."""
    file_path = []
    if files:
        try:
            for file in files[:1]:
                file_name = file.name
                path_to_upload = os.path.join(settings.MEDIA_ROOT, file_name)
                if not os.path.exists(settings.MEDIA_ROOT):
                    os.mkdir('media')
                file_path.append(file_name)
                path_to_upload = open(path_to_upload, 'wb+')
                file_data = file.chunks()
                for data in file_data:
                    path_to_upload.write(data)
        except:
            pass

    return file_path


async def update_live_feed(data, request):
    """
    Take the input, creates a connection to socket server.
    Send the data to the server
    """
    async with websockets.connect(
            'ws://localhost:8765') as websocket:
        try:
            article = ArticleGETSerializer(data).data
            likers = [like.get('username')
                      for like in article.get('likers')]
            if request.user.username in likers:
                article['liked'] = True
            else:
                article['liked'] = False
            result = json.dumps(article)
            await websocket.send(result)
            print('Sent....')
        except:
            pass
