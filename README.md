# Snapzy

Snapzy is a modern, full-featured social media platform built with Django and Tailwind CSS. It offers a vibrant, mobile-first user experience with features like posts, comments, likes, replies, user profiles, messaging, friend requests, privacy controls, and more.

## Features
- Responsive, colorful UI with Tailwind CSS
- User registration, login, and profile management
- Create, edit, and delete posts with images and videos
- Like and comment on posts (AJAX-powered)
- Reply to comments, like replies
- Follow/unfollow users, friend requests, and mutuals
- Privacy controls for profiles and posts
- Direct messaging and conversation views
- Search for users and follow/unfollow from results
- View lists of followers, following, and mutual friends
- Dynamic likes/comments lists with profile actions
- Modern navigation, mobile menu, and sticky footer

## Screenshots
> Add screenshots of the home, post, profile, and mobile views here.

## Tech Stack
- **Backend:** Django 4+
- **Frontend:** Tailwind CSS (CDN or built)
- **Database:** SQLite (default, easy to switch to Postgres)
- **Deployment:** Render (full Django), Netlify (static, for frontend-only)

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
6. **Access Snapzy:**
   Open [http://localhost:8000](http://localhost:8000) in your browser.

### Environment Variables
Create a `.env` file or set these in your deployment environment:
- `SECRET_KEY` (Django secret key)
- `DEBUG` (set to `False` in production)
- `ALLOWED_HOSTS` (comma-separated, e.g. `snapzy.onrender.com,localhost,127.0.0.1`)
- `DATABASE_URL` (for production/Postgres)

### Static & Media Files
- **Static files:**
  - Collected to `/static/` for deployment (`python manage.py collectstatic`)
- **Media files:**
  - Uploaded images/videos stored in `/media/`

### Tailwind CSS
- Uses Tailwind CDN for rapid prototyping.
- For production, consider integrating [django-tailwind](https://django-tailwind.readthedocs.io/) or building your own CSS for purging unused styles.

## Deployment

### Render (Recommended for Full Django)
- Add your environment variables in the Render dashboard.
- Set build/start commands:
  - **Build:** `python manage.py collectstatic --noinput`
  - **Start:** `gunicorn Social.wsgi`
- Add your Render domain to `ALLOWED_HOSTS`.
- Ensure static/media files are served (see Render docs).

### Netlify (Static Frontend Only)
- Not recommended for full Django apps (use for static builds only).
- For full functionality, deploy on Render, Heroku, or similar.

## Customization
- Update branding, colors, and logos in `base.html` and Tailwind classes.
- Add new features or templates as needed.

## Credits
- Built with [Django](https://www.djangoproject.com/) and [Tailwind CSS](https://tailwindcss.com/).
- UI/UX inspired by modern social platforms.

## License
[MIT](LICENSE)
