from django import forms
from .models import Post, Comment, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'post_caption']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What\'s on your mind?'}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'accept': 'video/*'}),
            'post_caption': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a caption...'}),
        }

    def save(self, commit=True):
        post = super().save(commit=False)
        video_file = self.cleaned_data.get('video')
        if video_file:
            from moviepy.editor import VideoFileClip
            from django.core.files.base import ContentFile
            import os
            import tempfile
            # Save the video file temporarily if not already saved
            if not post.video:
                post.video = video_file
                if commit:
                    post.save()
            # Generate thumbnail
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                    for chunk in video_file.chunks():
                        temp_video.write(chunk)
                    temp_video.flush()
                    clip = VideoFileClip(temp_video.name)
                    frame = clip.get_frame(0)  # Get first frame
                    import numpy as np
                    from PIL import Image
                    import io
                    image = Image.fromarray(np.uint8(frame))
                    thumb_io = io.BytesIO()
                    image.save(thumb_io, format='JPEG')
                    thumb_file = ContentFile(thumb_io.getvalue(), name=os.path.splitext(video_file.name)[0] + '_thumb.jpg')
                    post.video_thumbnail = thumb_file
                    clip.close()
            except Exception as e:
                print('Thumbnail generation failed:', e)
        if commit:
            post.save()
        return post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }

class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label='Username')
    bio = forms.CharField(
        required=False,
        max_length=200,
        help_text='Max 200 characters.',
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'w-full rounded-lg border border-gray-300 bg-white text-sm'
        })
    )
    contact_info = forms.CharField(
        required=False,
        max_length=100,
        help_text='Max 100 characters.',
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'w-full rounded-lg border border-gray-300 bg-white text-sm'
        })
    )

    class Meta:
        model = Profile
        fields = ['username', 'bio', 'profile_image', 'contact_info', 'privacy']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.setdefault('initial', {})
            initial['username'] = instance.user.username
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        profile = super().save(commit=False)
        username = self.cleaned_data['username']
        if profile.user.username != username:
            profile.user.username = username
            profile.user.save()
        if commit:
            profile.save()
        return profile 

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user 