from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from collections import defaultdict
from datetime import datetime, timezone

def now():
  return datetime.now(timezone.utc)

# User Data Schema
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  address = models.OneToOneField('Address', on_delete=models.CASCADE, null=True)
  projects = models.ManyToManyField('Project', through='Member', related_name="memberships")
  chat_channels = models.ManyToManyField('ChatChannel', related_name="channels")
  chats = models.ManyToManyField('ChatChannel', related_name="chats", through='Chat')
  friends = models.ManyToManyField("self", through='Friend')
  bio = models.CharField(max_length=1000, null=True, default="")
  telephone_number = models.DecimalField(max_digits=11, decimal_places=0, null=True)
  applications = models.ManyToManyField('Role', through='Application', related_name="role_application")

  def get_resume(self):
    skillset = defaultdict(float)
    for membership in self.member_set.all():
      end_date = membership.end_date
      if end_date == None:
        end_date = datetime.now(timezone.utc)
      start_date = membership.start_date
      duration = (end_date - start_date).total_seconds() / 3600
      for role in membership.roles.all():
        for skill in role.skills.all():
          skillset[skill] += duration
    return [(skill, round(skillset[skill], 2)) for skill in skillset]
  
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
  start_date = models.DateTimeField(default=now)
  end_date = models.DateTimeField(null=True)
  active = models.BooleanField(default=True)

  def applicable_role_list(self, user):
    roles = []
    for role in self.role_set.all():
      is_applicable = True
      if not user.is_authenticated:
        is_applicable = False
      else:
        membership = False
        if self.member_set.filter(profile=user.profile):
          membership = self.member_set.get(profile=user.profile)
        if role in map(lambda a: a.role, user.profile.application_set.filter(~(Q(status='R') | Q(status='D')))):
          is_applicable = False
        if membership and role in membership.roles.all():
          is_applicable = False
        roles.append((role, is_applicable))
    return roles

  def deactivate(self):
    self.active = False
    if self.end_date == None:
      self.end_date = now()
    for member in self.member_set.all():
      member.deactivate()
    for role in self.role_set.all():
      for app in role.application_set.all():
        app.delete()
    self.save()

  def set_creator(self, creator):
    new_role = Role.objects.create(project=self, title="Creator", description="Creator of the project.")
    creator.profile.projects.add(self, through_defaults={"is_owner": True, "start_date": datetime.now(timezone.utc)})
    membership = creator.profile.member_set.get(project=self)
    membership.roles.add(new_role)

class Member(models.Model):
  profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  roles = models.ManyToManyField('Role')
  is_owner = models.BooleanField()
  start_date = models.DateTimeField()
  end_date = models.DateTimeField(null=True)
  active = models.BooleanField(default=True)

  def deactivate(self):
    self.active = False
    self.end_date = now()
    self.save()

class Role(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  skills = models.ManyToManyField('Skill')
  title = models.CharField(max_length=45)
  description = models.CharField(max_length=1000)

  def __str__(self):
    return self.title

class Application(models.Model):
  applicant = models.ForeignKey(Profile, on_delete=models.CASCADE)
  role = models.ForeignKey(Role, on_delete=models.CASCADE)
  status = models.CharField(max_length=1, choices=(
    ('A', 'Applied'),
    ('O', 'Offered'),
    ('R', 'Rejected'),
    ('D', 'Declined')
  ))

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