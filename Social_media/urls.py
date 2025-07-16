from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profiles
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Lists
    path('profile/<str:username>/friends/', views.friends_list_view, name='friends_list'),
    path('profile/<str:username>/posts/', views.posts_list_view, name='posts_list'),
    path('profile/<str:username>/following/', views.following_list_view, name='following_list'),
    path('profile/<str:username>/followers/', views.followers_list_view, name='followers_list'),
    
    # Posts
    path('create-post/', views.create_post, name='create_post'),
    path('update-post/<int:post_id>/', views.update_post, name='update_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('post-likes/<int:post_id>/', views.post_likes_view, name='post_likes'),
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('like-comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('add-reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('like-reply/<int:reply_id>/', views.like_reply, name='like_reply'),
    
    # Friend Requests
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),
    
    # Following/Followers
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    
    # Messaging
    path('messages/', views.messages_view, name='messages'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
    
    # Search
    path('search/', views.search_users, name='search'),
    path('ajax/post-likes/<int:post_id>/', views.ajax_post_likes, name='ajax_post_likes'),
    path('ajax/post-comments/<int:post_id>/', views.ajax_post_comments, name='ajax_post_comments'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('change-password/', views.change_password, name='change_password'),
    path('multi-post/', views.multi_post_create, name='multi_post_create'),
] 