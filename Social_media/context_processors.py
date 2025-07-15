from django.utils import timezone

def profile_updates(request):
       if request.user.is_authenticated and hasattr(request.user, 'profile'):
           profile = request.user.profile
           return {
               'profile_updates': {
                   'date_created': profile.date_created,
                   'date_updated': profile.date_updated,
                   'date_active': profile.date_active,
                   'last_username_change': profile.last_username_change,
                   'timezone': timezone.get_current_timezone_name(),
               }
           }
       return {}