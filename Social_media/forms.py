from django import forms
from .models import Post, Comment, Profile
from django.contrib.auth.models import User

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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }

class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label='Username')

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