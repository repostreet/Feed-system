# Third party import
from django.urls import path, re_path

# App level import
from .views import (
    home
)

from .api import (
    AuthenticationAPI, RegistrationAPI,
    ArticlePostAPI, FeedGetAPI, LikeAPIView, CommentPostAPI,
    NotificationGetAPI, SearchAPI, upload_file
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', AuthenticationAPI.as_view(), name='sign_in'),
    path('registration/', RegistrationAPI.as_view(), name='registration_api'),
    path('create-article/', ArticlePostAPI.as_view(), name='create_article'),
    path('live-feed/', FeedGetAPI.as_view(), name='live_feed'),
    path('comment/', CommentPostAPI.as_view(), name='create_comment'),
    path('like/', LikeAPIView.as_view(), name='create_like'),
    re_path('upload-file/(?P<id>[\w]+)/', upload_file, name='upload_image'),
    re_path('search/(?P<query>[\w]+)/(?P<type>[\w]+)/$', SearchAPI.as_view(), name='search_api'),
    path('notification/', NotificationGetAPI.as_view(),
         name='fetch_notification')
]
