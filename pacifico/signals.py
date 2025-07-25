from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Only try to save the userprofile if it exists
        try:
            if hasattr(instance, 'userprofile'):
                instance.userprofile.save()
        except UserProfile.DoesNotExist:
            # Create a profile if it doesn't exist
            UserProfile.objects.create(user=instance)