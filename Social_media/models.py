from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    contact_info = models.TextField(blank=True, null=True)
    privacy = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_active = models.DateTimeField(default=timezone.now)
    last_username_change = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['sender', 'receiver']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    post_caption = models.TextField(blank=True, null=True)
    post_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-post_date']
    
    def __str__(self):
        return f"{self.user.username}'s post on {self.post_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def comment_count(self):
        return self.comments.count()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    likes_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.user.username}'s post"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['comment_date']
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.user.username}'s post"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    message_seen = models.BooleanField(default=False)
    sent_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sent_date']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.message[:50]}..."

class Reply(models.Model):
    reply_text = models.TextField()
    reply_date = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_replies')

    class Meta:
        ordering = ['reply_date']
        verbose_name_plural = 'Replies'

    def __str__(self):
        return f"Reply by {self.user.username} on {self.comment.id}"

    @property
    def like_count(self):
        return self.reply_likes.count()

class CommentLike(models.Model):
    like_date = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment_likes')

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"

class ReplyLike(models.Model):
    like_date = models.DateTimeField(auto_now_add=True)
    reply = models.ForeignKey('Reply', on_delete=models.CASCADE, related_name='reply_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reply_likes')

    class Meta:
        unique_together = ('user', 'reply')

    def __str__(self):
        return f"{self.user.username} likes reply {self.reply.id}"

class Follow(models.Model):
    follow_date = models.DateTimeField(auto_now_add=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
