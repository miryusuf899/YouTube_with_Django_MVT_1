from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Video, Comment, Like, Subscription, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'date_joined', 'is_staff')
    search_fields = ('username', 'email')
    list_filter   = ('is_staff', 'is_active')
    fieldsets     = UserAdmin.fieldsets + (
        ('Профиль', {'fields': ('avatar', 'cover', 'description')}),
    )

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display   = ('title', 'author', 'views', 'created_at')
    search_fields  = ('title', 'author__username')
    list_filter    = ('created_at',)
    readonly_fields = ('views', 'created_at')
    ordering       = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('user', 'video', 'created_at')
    search_fields = ('user__username', 'text')
    ordering      = ('-created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'value')
    list_filter  = ('value',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('subscriber', 'channel', 'created_at')
    search_fields = ('subscriber__username', 'channel__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('recipient', 'sender', 'message', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    ordering      = ('-created_at',)