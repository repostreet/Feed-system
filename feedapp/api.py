# Core import
import threading
from collections import defaultdict

# Third party import
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

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
from .utils import upload_handler


class ArticlePostAPI(APIView):

    def post(self, request, format=None):
        files = request.FILES.getlist('files')
        serilized_data = ArticlePOSTSerializer(data=request.data)

        file_upload_thread = threading.Thread(
            target=upload_handler, args=(files,))
        file_upload_thread.start()

        if serilized_data.is_valid():
            article_instance = serilized_data.save()
            article_instance.written_by = request.user
            article_instance.save()
            response = SUCCESS_MESSAGE.get('article')
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
                notification_type='LIKE',
                user_instance=article_instance.written_by,
                article_instance=article_instance,
                engager_name=request.user
            )
            response = SUCCESS_MESSAGE.get('like')
            status_code = status.HTTP_200_OK

        except (IntegrityError, Article.DoesNotExist) as e:
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
                notification_type='COMMENT',
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
                response['message'] = 'Check your email and password.'

        except (User.DoesNotExist,) as e:
            response['error'] = 'Check your email or password.'
            print(e)

        return Response(response, status=status_code)


class RegistrationAPI(APIView):

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
        article_instances = Article.objects.filter(body__contains=text)
        result = ArticleGETSerializer(article_instances, many=True)
        return result.data

    def get_person_search(self, text):
        user_instances = User.objects.filter(username=text)
        result = [{'username': user.username} for user in user_instances]
        return result
