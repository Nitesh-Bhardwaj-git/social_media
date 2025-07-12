from django.contrib import admin
from .models import Profile, FriendRequest, Post, Like, Comment, Message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_created', 'date_active']
    search_fields = ['user__username', 'user__email']
    list_filter = ['date_created', 'date_active']

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status', 'request_date']
    list_filter = ['status', 'request_date']
    search_fields = ['sender__username', 'receiver__username']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_caption', 'post_date', 'like_count', 'comment_count']
    list_filter = ['post_date']
    search_fields = ['user__username', 'post_caption', 'content']
    readonly_fields = ['like_count', 'comment_count']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'likes_date']
    list_filter = ['likes_date']
    search_fields = ['user__username', 'post__post_caption']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'comment_text', 'comment_date']
    list_filter = ['comment_date']
    search_fields = ['user__username', 'comment_text', 'post__post_caption']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'message_seen', 'sent_date']
    list_filter = ['message_seen', 'sent_date']
    search_fields = ['sender__username', 'receiver__username', 'message']
