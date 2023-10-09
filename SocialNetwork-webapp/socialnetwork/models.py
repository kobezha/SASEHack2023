# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    growth_points = models.IntegerField()
    streak = models.IntegerField()
    most_recent_diary_date = models.DateTimeField()

    def __unicode__(self):
        return self.user.username+','+self.bio+',end'

# Everytime the User class create a new instance, so does the Profile class.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, streak=0, most_recent_diary_date=timezone.now(), growth_points=0)

#Everytime the User instance is saved, so does the Profile class
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Post(models.Model):
    title = models.CharField(max_length=300)
    content       = models.CharField(max_length=300)
    created_by    = models.ForeignKey(User, related_name="post_creators", on_delete=models.PROTECT)
    creation_time = models.DateTimeField()
    created_by_username = models.CharField(max_length=100)
    created_by_identity = models.CharField(max_length=300)
    num_relates = models.IntegerField()
    num_hugs = models.IntegerField()
    num_comments = models.IntegerField()

    def __unicode__(self):
        return 'Post(id=' + str(self.content) + ')'

# Data model for a todo-list item
class Comment(models.Model):
    content       = models.CharField(max_length=300)
    created_by    = models.ForeignKey(User, related_name="comment_creators", on_delete=models.PROTECT)
    creation_time = models.DateTimeField()
    post          = models.ForeignKey(Post, related_name="comments", on_delete=models.PROTECT)
    created_by_username = models.CharField(max_length=100)

    def __unicode__(self):
        return self.content

class Relate(models.Model):
    post = models.ForeignKey(Post, related_name="relates", on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        unique_together = ['post', 'user']  # Ensures a user can only have one reaction per post
class Hug(models.Model):
    post = models.ForeignKey(Post, related_name="hugs", on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        unique_together = ['post', 'user']  # Ensures a user can only have one reaction per post