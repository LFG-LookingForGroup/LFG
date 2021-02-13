from django.db import models
from django.contrib.auth.models import User

# User Data Schema
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  address = models.OneToOneField('Address', on_delete=models.CASCADE)
  projects = models.ManyToManyField('Project', through='Member')
  chat_channels = models.ManyToManyField('ChatChannel', related_name="channels")
  chats = models.ManyToManyField('ChatChannel', related_name="chats", through='Chat')
  friends = models.ManyToManyField("self", through='Friend')
  bio = models.CharField(max_length=1000)
  telephone_number = models.DecimalField(max_digits=11, decimal_places=0)

class Address(models.Model):
  address1 = models.CharField(max_length=45)
  address2 = models.CharField(max_length=45)
  apartment_number = models.CharField(max_length=45)
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
  startDate = models.DateField()
  endDate = models.DateField()

class Member(models.Model):
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  role = models.ForeignKey('Role', on_delete=models.CASCADE)
  is_owner = models.BooleanField()
  startDate = models.DateField()
  endDate = models.DateField()

class Role(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  skills = models.ManyToManyField('Skill')
  title = models.CharField(max_length=45)
  description = models.CharField(max_length=1000)

class Skill(models.Model):
  parent = models.ForeignKey("self", on_delete=models.CASCADE)
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=250)

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