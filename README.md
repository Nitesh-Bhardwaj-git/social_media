# Snapzy - Social Media Platform

A modern, feature-rich social media platform built with Django that allows users to connect, share content, and interact with each other.

## 🌟 Features

### User Management
- **User Registration & Authentication**: Secure user registration and login system
- **Profile Management**: Customizable user profiles with bio, profile images, and privacy settings
- **Password Management**: Change password functionality
- **Privacy Controls**: Public/private profile settings

### Social Features
- **Friend System**: Send, accept, and reject friend requests
- **Follow System**: Follow/unfollow other users
- **User Search**: Search for users by username

### Content Sharing
- **Posts**: Create, edit, and delete posts with text content
- **Image Support**: Upload images with posts
- **Multi-Post Creation**: Create multiple posts at once
- **Post Feed**: View posts from friends and followed users

### Interaction Features
- **Likes**: Like posts, comments, and replies
- **Comments**: Add comments to posts
- **Replies**: Reply to comments with threaded discussions
- **Real-time Updates**: AJAX-powered like and comment updates

### Messaging
- **Direct Messages**: Private messaging between users
- **Conversation View**: Organized message threads
- **Message Status**: Track read/unread messages

### Additional Features
- **Notifications**: Stay updated with user activities
- **Responsive Design**: Mobile-friendly interface
- **File Upload**: Support for profile images and post images

## 🛠️ Technology Stack

- **Backend**: Django 5.2+
- **Database**: PostgreSQL (Neon Database)
- **File Storage**: Local file system with Pillow for image processing
- **Frontend**: HTML, CSS, JavaScript with AJAX
- **Deployment**: Render.com with WhiteNoise for static files
- **Environment**: Python-dotenv for environment variables

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- PostgreSQL database (or SQLite for development)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Snapzy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=your-database-url
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and go to `http://127.0.0.1:8000/`



## 🗄️ Database Models

### Core Models
- **User**: Django's built-in User model
- **Profile**: Extended user profile with bio, image, and privacy settings
- **Post**: User posts with content and images
- **Comment**: Comments on posts
- **Reply**: Replies to comments
- **Message**: Direct messages between users

### Social Models
- **FriendRequest**: Friend request system
- **Follow**: Follow/unfollow relationships
- **Like**: Post, comment, and reply likes

## 🔧 Configuration

### Development Settings
- Set `DEBUG = True` in settings.py
- Use SQLite database for local development
- Configure local media storage

### Production Settings
- Set `DEBUG = False`
- Use PostgreSQL database
- Configure proper static file serving
- Set up environment variables for sensitive data

## 🚀 Deployment

### Deploy to Render.com

1. **Connect your repository** to Render
2. **Create a new Web Service**
3. **Configure environment variables**:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `DEBUG=False`
4. **Set build command**: `pip install -r requirements.txt`
5. **Set start command**: `gunicorn Social.wsgi:application`

### Environment Variables for Production
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=your-production-database-url
ALLOWED_HOSTS=your-domain.com
```


### Authentication
- `GET/POST /register/` - User registration
- `GET/POST /login/` - User login
- `GET /logout/` - User logout

### Profiles
- `GET /profile/<username>/` - View user profile
- `GET/POST /edit-profile/` - Edit user profile

### Posts
- `GET/POST /create-post/` - Create new post
- `GET/POST /update-post/<id>/` - Update post
- `GET /delete-post/<id>/` - Delete post
- `GET /like-post/<id>/` - Like/unlike post

### Social Features
- `GET /send-friend-request/<id>/` - Send friend request
- `GET /follow/<id>/` - Follow user
- `GET /messages/` - View messages
- `GET /search/` - Search users

