from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# User Data Schema
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  address = models.OneToOneField('Address', on_delete=models.CASCADE, null=True)
  projects = models.ManyToManyField('Project', through='Member')
  chat_channels = models.ManyToManyField('ChatChannel', related_name="channels")
  chats = models.ManyToManyField('ChatChannel', related_name="chats", through='Chat')
  friends = models.ManyToManyField("self", through='Friend')
  bio = models.CharField(max_length=1000, null=True)
  telephone_number = models.DecimalField(max_digits=11, decimal_places=0, null=True)
  applicant = models.ManyToManyField('Project', through='Role')
  
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

class Address(models.Model):
  address_1 = models.CharField(max_length=45)
  address_2 = models.CharField(max_length=45, null=True)
  apartment_number = models.CharField(max_length=45, null=True)
  city = models.CharField(max_length=45)
  state = models.CharField(max_length=45)
  zipcode = models.CharField(max_length=45)
  country = models.CharField(max_length=45)

class Friend(models.Model):
  requestor = models.ForeignKey(Profile, related_name="requestor", on_delete=models.CASCADE)
  reciever = models.ForeignKey(Profile, related_name="reciever", on_delete=models.CASCADE)
  request_status = models.CharField(max_length=2, choices=[('RQ', 'Requested'), ('AC', 'Accepted'), ('RJ', 'Rejected')])

# Project Membership & Role Schema
class Project(models.Model):
  channels = models.ManyToManyField('ChatChannel', through='ProjectChannel')
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=10000)
  start_date = models.DateField(null=True)
  end_date = models.DateField(null=True)

class Member(models.Model):
  profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  roles = models.ManyToManyField('Role')
  is_owner = models.BooleanField()
  start_date = models.DateField()
  end_date = models.DateField(null=True)

class Role(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  skills = models.ManyToManyField('Skill')
  title = models.CharField(max_length=45)
  description = models.CharField(max_length=1000)

class Skill(models.Model):
  parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=250)

  def __str__(self):
    return self.name

# Chat Schema
class Chat(models.Model):
  sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name = 'sender_user')
  channel = models.ForeignKey('ChatChannel', on_delete=models.CASCADE)
  message = models.CharField(max_length = 2000)
  time_sent = models.DateTimeField(auto_now = True)
  
class ChatChannel(models.Model):
  channel_type = models.CharField(max_length=1, choices=[('D', 'Direct'), ('P', 'Project')])
  
class ProjectChannel(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  channel = models.ForeignKey(ChatChannel, on_delete=models.CASCADE)
  name = models.CharField(max_length = 45)