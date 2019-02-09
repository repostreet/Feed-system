# Third party import
from django.contrib import admin

# App level import
from .models import (
    Article, Comment, Notification
)

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Notification)
