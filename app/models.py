from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    cover = models.ImageField(upload_to='covers/', blank=True)
    description = models.TextField(blank=True)

class ActiveVideoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=True)

class Video(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)          # ← новое поле

    objects = ActiveVideoManager()       # по умолчанию только активные
    all_objects = models.Manager()       # все, включая удалённые

    def soft_delete(self):
        self.status = False
        self.save()

    def hard_delete(self):
        self.delete() 

    def restore(self):
        self.status = True
        self.save()

class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    class Meta:
        unique_together = ('video', 'user')

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    channel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('subscriber', 'channel')

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)