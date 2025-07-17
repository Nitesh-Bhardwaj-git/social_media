from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Profile, Post, Like, Comment, CommentLike, Reply, FriendRequest, Message, Follow, ReplyLike, PostImage
from .forms import PostForm, CommentForm, ProfileForm, CustomUserCreationForm
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from django.http import JsonResponse
from django.db import models
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import update_session_auth_hash
from django import forms
from django.contrib.auth import password_validation
from django.core.mail import send_mail

class SimplePasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if len(password1) < 6:
            raise forms.ValidationError('Password must be at least 6 characters long.')
        return password1
    def clean_new_password2(self):
        password2 = self.cleaned_data.get('new_password2')
        password1 = self.cleaned_data.get('new_password1')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The two password fields didn’t match.')
        # Do NOT call Django's default password validation
        return password2

def home(request):
    """Home page - shows all posts from all users"""
    if request.user.is_authenticated:
        # Get all posts
        all_posts = Post.objects.all().order_by('-post_date')
        
        # Filter posts based on privacy settings
        visible_posts = []
        for post in all_posts:
            # Get the post author's profile
            profile, created = Profile.objects.get_or_create(user=post.user)
            
            # If it's the user's own post, always show it
            if post.user == request.user:
                visible_posts.append(post)
            # If the profile is public, show the post
            elif profile.privacy == 'public':
                visible_posts.append(post)
            # If the profile is private, check if there's mutual following
            elif profile.privacy == 'private':
                # Check if current user is following the post author
                is_following_author = Follow.objects.filter(
                    follower=request.user, 
                    following=post.user
                ).exists()
                
                # Check if post author is following current user
                is_followed_by_author = Follow.objects.filter(
                    follower=post.user, 
                    following=request.user
                ).exists()
                
                # Only show post if there's mutual following
                if is_following_author and is_followed_by_author:
                    visible_posts.append(post)
        
        # Add like status for each visible post
        for post in visible_posts:
            post.is_liked = Like.objects.filter(user=request.user, post=post).exists()
            post.comments_with_likes = []
            for comment in post.comments.all():
                comment.is_liked = CommentLike.objects.filter(user=request.user, comment=comment).exists()
                comment.replies_with_likes = []
                for reply in comment.replies.all():
                    reply.is_liked = ReplyLike.objects.filter(user=request.user, reply=reply).exists()
                    comment.replies_with_likes.append(reply)
                post.comments_with_likes.append(comment)
            post.likes_list = Like.objects.filter(post=post).select_related('user')
        
        paginator = Paginator(visible_posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Add pending friend request count
        pending_friend_requests_count = FriendRequest.objects.filter(receiver=request.user, status='pending').count()

        # Notifications
        # 1. Latest likes on user's posts
        my_posts = Post.objects.filter(user=request.user)
        latest_likes = Like.objects.filter(post__in=my_posts).order_by('-likes_date')[:5]
        # 2. Latest comments on user's posts
        latest_comments = Comment.objects.filter(post__in=my_posts).order_by('-comment_date')[:5]
        # 3. Pending follow requests
        latest_follow_requests = FriendRequest.objects.filter(receiver=request.user, status='pending').order_by('-request_date')[:5]
        # 4. New posts from people I follow
        following_ids = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        latest_friend_posts = Post.objects.filter(user__in=following_ids).exclude(user=request.user).order_by('-post_date')[:5]

        notifications = {
            'likes': latest_likes,
            'comments': latest_comments,
            'follow_requests': latest_follow_requests,
            'friend_posts': latest_friend_posts,
        }
    else:
        page_obj = []
        pending_friend_requests_count = 0
        notifications = None
    context = {
        'page_obj': page_obj,
        'posts': page_obj,
        'pending_friend_requests_count': pending_friend_requests_count,
        'notifications': notifications,
    }
    return render(request, 'Social_media/home.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for new user
            Profile.objects.create(user=user)
            # Send welcome email
            send_mail(
                subject='Welcome to Snapzy!',
                message=f'Hello {user.username},\n\nYour account has been created successfully on Snapzy.\n\nThank you for joining us!',
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[user.email],
                fail_silently=False,
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'Social_media/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'The username or password is incorrect.')
        else:
            messages.error(request, 'The username or password is incorrect.')
    else:
        form = AuthenticationForm()
    return render(request, 'Social_media/login.html', {'form': form})

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile_view(request, username):
    """User profile view"""
    user = get_object_or_404(User, username=username)
    
    # Check if user has a profile, create one if not
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Check privacy settings
    is_private = profile.privacy == 'private'
    is_own_profile = request.user == user
    
    # Check if current user is following the profile owner
    is_following = False
    if not is_own_profile:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    # Check if profile owner is following current user (for mutual following check)
    is_followed_by = False
    if not is_own_profile:
        is_followed_by = Follow.objects.filter(follower=user, following=request.user).exists()
    
    # Check for pending friend requests
    has_pending_request = False
    if not is_own_profile:
        has_pending_request = FriendRequest.objects.filter(
            sender=request.user,
            receiver=user,
            status='pending'
        ).exists()
    
    # Determine if posts should be shown
    show_posts = True
    if is_private and not is_own_profile:
        # For private profiles, only show posts if there's mutual following
        show_posts = is_following and is_followed_by
    
    # If private account and not mutual followers/owner, show limited profile
    if is_private and not is_own_profile and not (is_following and is_followed_by):
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(following=user).count()
        posts_count = Post.objects.filter(user=user).count()
        context = {
            'profile_user': user,
            'is_private': True,
            'posts': [],
            'following_count': following_count,
            'followers_count': followers_count,
            'posts_count': posts_count,
            'is_following': is_following,
            'is_followed_by': is_followed_by,
            'has_pending_request': has_pending_request,
            'message_count': 0,  # No messages if not mutual
        }
        return render(request, 'Social_media/profile.html', context)
    
    # Get posts based on privacy settings
    if show_posts:
        posts = Post.objects.filter(user=user).order_by('-post_date')
        
        # Add like status for each post if user is authenticated
        if request.user.is_authenticated:
            for post in posts:
                post.is_liked = Like.objects.filter(user=request.user, post=post).exists()
                post.comments_with_likes = []
                for comment in post.comments.all():
                    comment.is_liked = CommentLike.objects.filter(user=request.user, comment=comment).exists()
                    comment.replies_with_likes = []
                    for reply in comment.replies.all():
                        reply.is_liked = ReplyLike.objects.filter(user=request.user, reply=reply).exists()
                        comment.replies_with_likes.append(reply)
                    post.comments_with_likes.append(comment)
                post.likes_list = Like.objects.filter(post=post).select_related('user')
    else:
        posts = []
    
    # Calculate following and followers counts
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()

    # Calculate unseen message count between logged-in user and profile user
    if request.user.is_authenticated and request.user != user:
        from .models import Message
        unseen_message_count = Message.objects.filter(
            sender=user, receiver=request.user, message_seen=False
        ).count()
    else:
        unseen_message_count = 0
    
    context = {
        'profile_user': user,
        'posts': posts,
        'following_count': following_count,
        'followers_count': followers_count,
        'is_following': is_following,
        'is_followed_by': is_followed_by,
        'has_pending_request': has_pending_request,
        'is_private': False,
        'message_count': unseen_message_count,
    }
    return render(request, 'Social_media/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    can_change_username = (
        not profile.last_username_change or
        timezone.now() - profile.last_username_change > timedelta(days=30)
    )
    username_error = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            if new_username != request.user.username:
                if can_change_username:
                    profile.last_username_change = timezone.now()
                    profile.user.username = new_username
                    profile.user.save()
                else:
                    username_error = 'You can only change your username once every 30 days.'
            if not username_error:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'Social_media/edit_profile.html', {'form': form, 'can_change_username': can_change_username, 'username_error': username_error})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            for f in files:
                PostImage.objects.create(post=post, image=f)
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'Social_media/create.html', {'form': form})

@login_required
def multi_post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            for f in files:
                PostImage.objects.create(post=post, image=f)
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'Social_media/multi_post_create.html', {'form': form})

@login_required
def like_post(request, post_id):
    """Like/unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # User already liked the post, so unlike it
        like.delete()
    
    # AJAX support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': created,
            'like_count': post.like_count,
        })
    
    # Get current URL parameters to maintain state
    show_comments = request.GET.get('show_comments')
    show_reply = request.GET.get('show_reply')
    
    # Build redirect URL to home with proper parameters and post anchor
    redirect_url = '/'
    if show_comments:
        redirect_url += f'?show_comments={show_comments}'
        if show_reply:
            redirect_url += f'&show_reply={show_reply}'
    
    # Add post anchor to maintain scroll position
    redirect_url += f'#post-{post_id}'
    
    return redirect(redirect_url)

@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
            # Always redirect to home page with show_comments parameter and post anchor
            return redirect(f'/?show_comments={post_id}#post-{post_id}')
    else:
        form = CommentForm()
    
    return render(request, 'Social_media/add_comment.html', {'form': form, 'post': post})

@login_required
def send_friend_request(request, user_id):
    """Send a friend request"""
    receiver = get_object_or_404(User, id=user_id)
    
    if request.user == receiver:
        messages.error(request, 'You cannot send a friend request to yourself!')
        return redirect('profile', username=receiver.username)
    
    # Check if friend request already exists
    friend_request, created = FriendRequest.objects.get_or_create(
        sender=request.user,
        receiver=receiver,
        defaults={'status': 'pending'}
    )
    
    if created:
        messages.success(request, f'Friend request sent to {receiver.username}!')
    else:
        messages.info(request, f'Friend request already sent to {receiver.username}.')
    
    return redirect('profile', username=receiver.username)

@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.status = 'accepted'
    friend_request.save()
    
    # Create follow relationship when friend request is accepted
    Follow.objects.get_or_create(
        follower=friend_request.sender,
        following=friend_request.receiver
    )
    
    messages.success(request, f'Friend request from {friend_request.sender.username} accepted! You are now following each other.')
    return redirect('friend_requests')

@login_required
def reject_friend_request(request, request_id):
    """Reject a friend request"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.status = 'rejected'
    friend_request.save()
    messages.info(request, f'Friend request from {friend_request.sender.username} rejected.')
    return redirect('friend_requests')

@login_required
def friend_requests(request):
    """View friend requests"""
    received_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
    sent_requests = FriendRequest.objects.filter(sender=request.user, status='pending')
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    return render(request, 'Social_media/friend_requests.html', context)

@login_required
def messages_view(request):
    """View messages"""
    user = request.user
    from .models import Message
    # Get all users who have sent or received messages with the current user
    sent_user_ids = Message.objects.filter(sender=user).values_list('receiver', flat=True)
    received_user_ids = Message.objects.filter(receiver=user).values_list('sender', flat=True)
    conversation_user_ids = set(sent_user_ids) | set(received_user_ids)
    # Exclude self from the list
    conversation_user_ids.discard(user.id)
    users = User.objects.filter(id__in=conversation_user_ids).select_related('profile')

    # Calculate unseen message counts for each user
    unseen_message_counts = {}
    for u in users:
        count = Message.objects.filter(sender=u, receiver=user, message_seen=False).count()
        unseen_message_counts[u.id] = count
    
    context = {
        'users': users,
        'message_counts': unseen_message_counts,
    }
    return render(request, 'Social_media/messages.html', context)

@login_required
def conversation_view(request, user_id):
    """View conversation with a specific user"""
    other_user = get_object_or_404(User, id=user_id)

    # --- Mutual follow and privacy check ---
    # Get the other user's profile
    other_profile, _ = Profile.objects.get_or_create(user=other_user)
    is_private = other_profile.privacy == 'private'
    is_own_profile = request.user == other_user

    # Check if current user is following the other user
    is_following = False
    if not is_own_profile:
        is_following = Follow.objects.filter(follower=request.user, following=other_user).exists()

    # Check if other user is following current user (for mutual following check)
    is_followed_by = False
    if not is_own_profile:
        is_followed_by = Follow.objects.filter(follower=other_user, following=request.user).exists()

    # If the other user's profile is private, only allow messaging if mutual follow or owner
    if is_private and not is_own_profile and not (is_following and is_followed_by):
        messages.error(request, 'You can only message this user if you both follow each other.')
        return redirect('profile', username=other_user.username)

    # --- End mutual follow and privacy check ---

    # Get all messages between the two users
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('sent_date')

    # Mark messages as seen
    Message.objects.filter(sender=other_user, receiver=request.user, message_seen=False).update(message_seen=True)

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                message=message_text
            )
            return redirect('conversation', user_id=user_id)

    context = {
        'other_user': other_user,
        'messages': messages_qs,
        'user': request.user,  # Add this line
    }
    return render(request, 'Social_media/conversation.html', context)

@login_required
def search_users(request):
    """Search for users"""
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
        
        # Add follow status for each user
        for user in users:
            user.is_following = Follow.objects.filter(follower=request.user, following=user).exists()
            user.is_followed_by = Follow.objects.filter(follower=user, following=request.user).exists()
            user.has_pending_request = FriendRequest.objects.filter(
                sender=request.user,
                receiver=user,
                status='pending'
            ).exists()
    
    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'Social_media/search.html', context)

@login_required
def update_post(request, post_id):
    """Update a post"""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('home')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'Social_media/update.html', context)

@login_required
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if request.method == 'POST':
        print("POST received for delete_post")  # DEBUG
        if request.POST.get('confirm_delete'):
            print(f"Confirmed delete for post: {post.id}")  # DEBUG
            post.delete()
            print(f"Post {post.id} deleted from DB")  # DEBUG
            messages.success(request, 'Post deleted successfully!')
            return redirect('home')
        else:
            print("Delete not confirmed (checkbox not checked)")  # DEBUG
            messages.error(request, 'Please confirm the deletion.')
    
    context = {
        'post': post,
    }
    return render(request, 'Social_media/delete.html', context)

@login_required
def friends_list_view(request, username):
    """View to display a user's friends list"""
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')
    
    # Check privacy settings
    profile, created = Profile.objects.get_or_create(user=profile_user)
    is_private = profile.privacy == 'private'
    is_own_profile = request.user == profile_user
    
    # Check if current user is friends with the profile owner
    is_friend = False
    if not is_own_profile:
        friends_sent = FriendRequest.objects.filter(sender=request.user, receiver=profile_user, status='accepted').exists()
        friends_received = FriendRequest.objects.filter(sender=profile_user, receiver=request.user, status='accepted').exists()
        is_friend = friends_sent or friends_received
    
    # If private account and not friend/owner, show limited view
    if is_private and not is_own_profile and not is_friend:
        context = {
            'profile_user': profile_user,
            'friends': [],
            'is_private': True,
        }
        return render(request, 'Social_media/friends_list.html', context)
    
    # Get all friends (accepted FriendRequests, both directions)
    friends_sent = FriendRequest.objects.filter(sender=profile_user, status='accepted').values_list('receiver', flat=True)
    friends_received = FriendRequest.objects.filter(receiver=profile_user, status='accepted').values_list('sender', flat=True)
    friend_ids = set(friends_sent) | set(friends_received)
    friends = User.objects.filter(id__in=friend_ids)
    
    context = {
        'profile_user': profile_user,
        'friends': friends,
        'is_private': False,
    }
    return render(request, 'Social_media/friends_list.html', context)

@login_required
def posts_list_view(request, username):
    """View to display a user's posts list"""
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')
    
    # Check privacy settings
    profile, created = Profile.objects.get_or_create(user=profile_user)
    is_private = profile.privacy == 'private'
    is_own_profile = request.user == profile_user
    
    # Check if current user is friends with the profile owner
    is_friend = False
    if not is_own_profile:
        friends_sent = FriendRequest.objects.filter(sender=request.user, receiver=profile_user, status='accepted').exists()
        friends_received = FriendRequest.objects.filter(sender=profile_user, receiver=request.user, status='accepted').exists()
        is_friend = friends_sent or friends_received
    
    # If private account and not friend/owner, show limited view
    if is_private and not is_own_profile and not is_friend:
        context = {
            'profile_user': profile_user,
            'posts': [],
            'is_private': True,
        }
        return render(request, 'Social_media/posts_list.html', context)
    
    posts = Post.objects.filter(user=profile_user).order_by('-post_date')
    
    # Add like status for each post if user is authenticated
    if request.user.is_authenticated:
        for post in posts:
            post.is_liked = Like.objects.filter(user=request.user, post=post).exists()
            post.comments_with_likes = []
            for comment in post.comments.all():
                comment.is_liked = CommentLike.objects.filter(user=request.user, comment=comment).exists()
                comment.replies_with_likes = []
                for reply in comment.replies.all():
                    reply.is_liked = ReplyLike.objects.filter(user=request.user, reply=reply).exists()
                    comment.replies_with_likes.append(reply)
                post.comments_with_likes.append(comment)
            post.likes_list = Like.objects.filter(post=post).select_related('user')
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_private': False,
    }
    return render(request, 'Social_media/posts_list.html', context)

@login_required
def post_likes_view(request, post_id):
    """View to display who liked a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Get all users who liked this post
    liked_users = User.objects.filter(user_likes__post=post).order_by('username')
    
    context = {
        'post': post,
        'liked_users': liked_users,
    }
    return render(request, 'Social_media/post_likes.html', context)

@login_required
def follow_user(request, user_id):
    """Follow or unfollow a user"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if request.user == user_to_follow:
        messages.error(request, 'You cannot follow yourself.')
        return redirect('profile', username=user_to_follow.username)
    
    # Get the profile of the user to follow
    profile, created = Profile.objects.get_or_create(user=user_to_follow)
    
    # Check if already following
    existing_follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    ).exists()
    
    if existing_follow:
        # Already following, so unfollow
        Follow.objects.filter(
            follower=request.user,
            following=user_to_follow
        ).delete()
        messages.success(request, f'You unfollowed {user_to_follow.username}.')
    else:
        # Check if the user has a private profile
        if profile.privacy == 'private':
            # Try to get or create a friend request regardless of status
            friend_request, created = FriendRequest.objects.get_or_create(
                sender=request.user,
                receiver=user_to_follow,
                defaults={'status': 'pending'}
            )
            if not created:
                if friend_request.status == 'pending':
                    messages.info(request, f'You already have a pending friend request to {user_to_follow.username}.')
                elif friend_request.status == 'accepted':
                    follow_exists = Follow.objects.filter(
                        follower=request.user,
                        following=user_to_follow
                    ).exists()
                    if follow_exists:
                        messages.info(request, f'You are already following {user_to_follow.username}.')
                    else:
                        # This should not happen unless the database is inconsistent.
                        # Reset the friend request to pending and allow resending.
                        friend_request.status = 'pending'
                        friend_request.save()
                        messages.success(request, f'Your previous request was not completed. Friend request re-sent to {user_to_follow.username}.')
                else:
                    # If previously rejected, allow resending
                    friend_request.status = 'pending'
                    friend_request.save()
                    messages.success(request, f'Friend request re-sent to {user_to_follow.username}.')
            else:
                messages.success(request, f'Friend request sent to {user_to_follow.username}. They need to accept your request.')
        else:
            # For public profiles, follow directly
            Follow.objects.create(
                follower=request.user,
                following=user_to_follow
            )
            messages.success(request, f'You are now following {user_to_follow.username}.')
    
    # Check if user came from search page and redirect back there
    referer = request.META.get('HTTP_REFERER', '')
    if 'search' in referer:
        # Extract the search query from the referer URL
        parsed_url = urlparse(referer)
        query_params = parse_qs(parsed_url.query)
        search_query = query_params.get('q', [''])[0]
        
        if search_query:
            return redirect(f'/search/?q={search_query}')
        else:
            return redirect('search')
    elif 'following' in referer or 'followers' in referer:
        # Extract the username from the referer URL to redirect back to the same list
        parsed_url = urlparse(referer)
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 3:
            username = path_parts[2]  # Get username from /profile/username/following/ or /profile/username/followers/
            if 'following' in referer:
                return redirect('following_list', username=username)
            elif 'followers' in referer:
                return redirect('followers_list', username=username)
    
    # Default redirect to profile
    return redirect('profile', username=user_to_follow.username)

@login_required
def unfollow_user(request, user_id):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    if request.user == user_to_unfollow:
        messages.error(request, 'You cannot unfollow yourself.')
        return redirect('profile', username=user_to_unfollow.username)
    
    # Check if following
    try:
        follow_relationship = Follow.objects.get(
            follower=request.user,
            following=user_to_unfollow
        )
        follow_relationship.delete()
        messages.success(request, f'You unfollowed {user_to_unfollow.username}.')
    except Follow.DoesNotExist:
        messages.error(request, f'You are not following {user_to_unfollow.username}.')
    
    # Check if user came from search page and redirect back there
    referer = request.META.get('HTTP_REFERER', '')
    if 'search' in referer:
        # Extract the search query from the referer URL
        parsed_url = urlparse(referer)
        query_params = parse_qs(parsed_url.query)
        search_query = query_params.get('q', [''])[0]
        
        if search_query:
            return redirect(f'/search/?q={search_query}')
        else:
            return redirect('search')
    elif 'following' in referer or 'followers' in referer:
        # Extract the username from the referer URL to redirect back to the same list
        parsed_url = urlparse(referer)
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 3:
            username = path_parts[2]  # Get username from /profile/username/following/ or /profile/username/followers/
            if 'following' in referer:
                return redirect('following_list', username=username)
            elif 'followers' in referer:
                return redirect('followers_list', username=username)
    
    # Default redirect to profile
    return redirect('profile', username=user_to_unfollow.username)

@login_required
def following_list_view(request, username):
    """View to display who a user is following"""
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')
    
    # Check privacy settings
    profile, created = Profile.objects.get_or_create(user=profile_user)
    is_private = profile.privacy == 'private'
    is_own_profile = request.user == profile_user
    
    # Check if current user is following the profile owner
    is_following = False
    if not is_own_profile:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    # If private account and not following/owner, show limited view
    if is_private and not is_own_profile and not is_following:
        context = {
            'profile_user': profile_user,
            'following_list': [],
            'is_private': True,
        }
        return render(request, 'Social_media/following_list.html', context)
    
    # Get all users that the profile_user is following
    following_ids = Follow.objects.filter(follower=profile_user).values_list('following', flat=True)
    following_list = User.objects.filter(id__in=following_ids).order_by('username')
    
    # Add follow status for current user
    for user in following_list:
        user.is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        user.is_followed_by = Follow.objects.filter(follower=user, following=request.user).exists()
    
    # Debug: Print the count of following
    print(f"DEBUG: {profile_user.username} is following {following_list.count()} users")
    for user in following_list:
        print(f"DEBUG: Following user: {user.username}")
    
    context = {
        'profile_user': profile_user,
        'following_list': following_list,
        'is_private': False,
    }
    return render(request, 'Social_media/following_list.html', context)

@login_required
def followers_list_view(request, username):
    """View to display a user's followers list"""
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')
    
    # Check privacy settings
    profile, created = Profile.objects.get_or_create(user=profile_user)
    is_private = profile.privacy == 'private'
    is_own_profile = request.user == profile_user
    
    # Check if current user is following the profile owner
    is_following = False
    if not is_own_profile:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    # If private account and not following/owner, show limited view
    if is_private and not is_own_profile and not is_following:
        context = {
            'profile_user': profile_user,
            'followers_list': [],
            'is_private': True,
        }
        return render(request, 'Social_media/followers_list.html', context)
    
    # Get all users who are following the profile_user
    follower_ids = Follow.objects.filter(following=profile_user).values_list('follower', flat=True)
    followers_list = User.objects.filter(id__in=follower_ids).order_by('username')
    
    # Add follow status for current user
    for user in followers_list:
        user.is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        user.is_followed_by = Follow.objects.filter(follower=user, following=request.user).exists()
    
    # Debug: Print the count of followers
    print(f"DEBUG: {profile_user.username} has {followers_list.count()} followers")
    for user in followers_list:
        print(f"DEBUG: Follower user: {user.username}")
    
    context = {
        'profile_user': profile_user,
        'followers_list': followers_list,
        'is_private': False,
    }
    return render(request, 'Social_media/followers_list.html', context)

@login_required
def like_comment(request, comment_id):
    """Like/unlike a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
    
    if not created:
        # User already liked the comment, so unlike it
        like.delete()
    
    # AJAX support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': created,
            'like_count': comment.comment_likes.count(),
        })
    # Get current URL parameters to maintain state
    show_comments = request.GET.get('show_comments')
    show_reply = request.GET.get('show_reply')
    
    # Build redirect URL to home with proper parameters and post anchor
    redirect_url = '/'
    if show_comments:
        redirect_url += f'?show_comments={show_comments}'
        if show_reply:
            redirect_url += f'&show_reply={show_reply}'
    
    # Add post anchor to maintain scroll position
    redirect_url += f'#post-{comment.post.id}'
    
    return redirect(redirect_url)

@login_required
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text', '').strip()
        if not reply_text:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'No reply text'}, status=400)
            return redirect('home')
        else:
            reply = Reply.objects.create(
                user=request.user,
                comment=comment,
                reply_text=reply_text
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            # Get current URL parameters to maintain state
            show_comments = request.GET.get('show_comments')
            show_reply = request.GET.get('show_reply')
            redirect_url = '/'
            if show_comments:
                redirect_url += f'?show_comments={show_comments}'
                if show_reply:
                    redirect_url += f'&show_reply={show_reply}'
            redirect_url += f'#post-{comment.post.id}'
            return redirect(redirect_url)
    # If GET request, show the reply form
    context = {
        'comment': comment,
    }
    return render(request, 'Social_media/add_reply.html', context)

@login_required
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    like, created = ReplyLike.objects.get_or_create(user=request.user, reply=reply)
    if not created:
        like.delete()
    # AJAX support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': created,
            'like_count': reply.reply_likes.count(),
        })
    # Get current URL parameters to maintain state
    show_comments = request.GET.get('show_comments')
    show_reply = request.GET.get('show_reply')
    # Build redirect URL to home with proper parameters and post anchor
    redirect_url = '/'
    if show_comments:
        redirect_url += f'?show_comments={show_comments}'
        if show_reply:
            redirect_url += f'&show_reply={show_reply}'
    # Add post anchor to maintain scroll position
    redirect_url += f'#post-{reply.comment.post.id}'
    return redirect(redirect_url)

@login_required
def ajax_post_likes(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    likes_list = Like.objects.filter(post=post).select_related('user')
    # Add follow status for each user in the likes list
    if request.user.is_authenticated:
        for like in likes_list:
            like.user.is_following = Follow.objects.filter(follower=request.user, following=like.user).exists()
            like.user.is_followed_by = Follow.objects.filter(follower=like.user, following=request.user).exists()
    html = render_to_string('Social_media/partials/likes_list.html', {'post': post, 'likes_list': likes_list}, request=request)
    return JsonResponse({'html': html})

@login_required
def ajax_post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related('user')
    # Add like status and follow status for each comment and reply, and build replies_with_likes
    if request.user.is_authenticated:
        for comment in comments:
            comment.is_liked = CommentLike.objects.filter(user=request.user, comment=comment).exists()
            comment.user.is_following = Follow.objects.filter(follower=request.user, following=comment.user).exists()
            comment.user.is_followed_by = Follow.objects.filter(follower=comment.user, following=request.user).exists()
            comment.replies_with_likes = []
            for reply in comment.replies.all():
                reply.is_liked = ReplyLike.objects.filter(user=request.user, reply=reply).exists()
                reply.user.is_following = Follow.objects.filter(follower=request.user, following=reply.user).exists()
                reply.user.is_followed_by = Follow.objects.filter(follower=reply.user, following=request.user).exists()
                comment.replies_with_likes.append(reply)
    html = render_to_string('Social_media/partials/comments_list.html', {'post': post, 'comments': comments}, request=request)
    return JsonResponse({'html': html})

def message_senders_count(request):
    if request.user.is_authenticated:
        from .models import Message
        # Count unique senders who have sent UNSEEN messages to the logged-in user
        count = Message.objects.filter(receiver=request.user, message_seen=False).values('sender').distinct().count()
        return {'message_senders_count': count}
    return {'message_senders_count': 0}

def pending_friend_requests_count_processor(request):
    if request.user.is_authenticated:
        return {
            'pending_friend_requests_count': FriendRequest.objects.filter(receiver=request.user, status='pending').count()
        }
    return {'pending_friend_requests_count': 0}

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Add like/comment/reply status if user is authenticated
    if request.user.is_authenticated:
        post.is_liked = Like.objects.filter(user=request.user, post=post).exists()
        post.comments_with_likes = []
        for comment in post.comments.all():
            comment.is_liked = CommentLike.objects.filter(user=request.user, comment=comment).exists()
            comment.replies_with_likes = []
            for reply in comment.replies.all():
                reply.is_liked = ReplyLike.objects.filter(user=request.user, reply=reply).exists()
                comment.replies_with_likes.append(reply)
            post.comments_with_likes.append(comment)
        post.likes_list = Like.objects.filter(post=post).select_related('user')
    context = {
        'post': post,
    }
    return render(request, 'Social_media/post_detail.html', context)

@login_required
def notifications_view(request):
    # 1. Latest likes on user's posts
    my_posts = Post.objects.filter(user=request.user)
    latest_likes = Like.objects.filter(post__in=my_posts).order_by('-likes_date')[:10]
    # 2. Latest comments on user's posts
    latest_comments = Comment.objects.filter(post__in=my_posts).order_by('-comment_date')[:10]
    # 3. Pending follow requests
    latest_follow_requests = FriendRequest.objects.filter(receiver=request.user, status='pending').order_by('-request_date')[:10]
    # 4. New posts from people I follow
    following_ids = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    latest_friend_posts = Post.objects.filter(user__in=following_ids).exclude(user=request.user).order_by('-post_date')[:10]

    notifications = {
        'likes': latest_likes,
        'comments': latest_comments,
        'follow_requests': latest_follow_requests,
        'friend_posts': latest_friend_posts,
    }
    return render(request, 'Social_media/notifications.html', {'notifications': notifications})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = SimplePasswordChangeForm(user=request.user, data=request.POST)
    else:
        form = SimplePasswordChangeForm(user=request.user)
    # Set autocomplete attributes for all password fields
    form.fields['old_password'].widget.attrs['autocomplete'] = 'current-password'
    form.fields['new_password1'].widget.attrs['autocomplete'] = 'new-password'
    form.fields['new_password2'].widget.attrs['autocomplete'] = 'new-password'
    form.fields['old_password'].widget.attrs['name'] = 'current_pass'
    form.fields['new_password1'].widget.attrs['name'] = 'new_pass1'
    form.fields['new_password2'].widget.attrs['name'] = 'new_pass2'
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            logout(request)
            messages.success(request, 'Your password was changed successfully. Please log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    return render(request, 'Social_media/change_password.html', {'form': form})
