# Third party import
from django.db import models
from django.contrib.auth.models import User


NOTIFICATION_TYPE = (
    ('Liked', 'Liked'),
    ('Commented', 'Commented')
)


class Article(models.Model):
    """
    Does the following thing given below.
    Creates an article instance which would contains two mandatory
    field i,e title & description and one optional media field_url.
    Another field likers stores the list of all user instances who
    have liked the article.
    """

    title = models.CharField(max_length=1000)
    body = models.CharField(max_length=1000)
    media_url = models.CharField(max_length=1000, null=True)
    written_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    likers = models.ManyToManyField(User, related_name='article_likers')
    contain_media = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.media_url:
            self.contain_media = True
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-timestamp', 'title']
        verbose_name = 'Posted article'
        verbose_name_plural = 'Posted article list'


class Comment(models.Model):
    """
    This table has a foriegnkey relationship field to the Article instance.
    The field name of which is article_instance and one more foriegnkey field
    which stores which article the comment belongs to.
    """

    # comment_body = models.CharField(max_length=100)
    # user_instance = models.Foriegnkey(User, on_delete=models.CASCADE)
    # article_instance = models.Foriegnkey(
    #     Article, on_delete=models.CASCADE, related_name='comment_list')

    comment_body = models.CharField(max_length=1000)
    user_username = models.CharField(max_length=1000)
    article_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user_username
        text = self.comment_body
        return '{} commented - {}'.format(username, text)

    class Meta:
        ordering = ['-pk', 'user_username']
        verbose_name = 'Posted comment'
        verbose_name_plural = 'Posted comment list'


class Notification(models.Model):
    """Create the notification instance for each user."""

    notification_type = models.CharField(
        max_length=10, choices=NOTIFICATION_TYPE)
    user_instance = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notification_list')
    article_instance = models.ForeignKey(Article, on_delete=models.CASCADE)
    engager_name = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_instance.username

    class Meta:
        ordering = ['-pk', 'user_instance__username']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notification list'
