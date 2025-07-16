from django import forms
from .models import Post, Comment, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from moviepy.editor import VideoFileClip


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'post_caption']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What\'s on your mind?'}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'post_caption': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a caption...'}),
        }

    def save(self, commit=True):
        post = super().save(commit=False)
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user 