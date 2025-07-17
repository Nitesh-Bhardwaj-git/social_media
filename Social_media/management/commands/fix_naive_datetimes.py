from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from pytz import timezone as pytz_timezone

from Social_media.models import Post, Message, Comment, Reply, Like, CommentLike, ReplyLike, FriendRequest, Follow, Profile

KOLKATA = pytz_timezone('Asia/Kolkata')

def make_aware_if_naive(dt):
    if timezone.is_naive(dt):
        # Assume dt is in Asia/Kolkata, convert to UTC
        aware = KOLKATA.localize(dt)
        return aware.astimezone(timezone.utc)
    return dt

class Command(BaseCommand):
    help = 'Convert all naive datetimes to UTC-aware, assuming they were originally in Asia/Kolkata.'

    @transaction.atomic
    def handle(self, *args, **options):
        models_and_fields = [
            (Post, ['post_date']),
            (Message, ['sent_date']),
            (Comment, ['comment_date']),
            (Reply, ['reply_date']),
            (Like, ['likes_date']),
            (CommentLike, ['like_date']),
            (ReplyLike, ['like_date']),
            (FriendRequest, ['request_date']),
            (Follow, ['follow_date']),
            (Profile, ['date_created', 'date_updated', 'date_active', 'last_username_change']),
        ]
        for model, fields in models_and_fields:
            for obj in model.objects.all():
                changed = False
                for field in fields:
                    dt = getattr(obj, field)
                    new_dt = make_aware_if_naive(dt)
                    if new_dt != dt:
                        setattr(obj, field, new_dt)
                        changed = True
                if changed:
                    obj.save(update_fields=fields)
        self.stdout.write(self.style.SUCCESS('All naive datetimes converted to UTC-aware!')) 