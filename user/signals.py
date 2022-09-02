import email
from unicodedata import name
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewUser

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='employee')
        instance.groups.add(group)
        NewUser.objects.create(
            user = instance,
            name = instance.first_name + ' ' +instance.last_name,
            email = instance.email,
            )
        print('New user created')
# post_save.connect(create_profile, sender=User)



# @receiver(post_save, sender=User)
# def update_profile(sender, instance, created, **kwargs):
#     if created == False:
#         instance.newuser.save()
#         print('New-user updated')
# # post_save.connect(update_profile, sender=User)