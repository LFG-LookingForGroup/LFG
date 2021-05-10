from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from collections import defaultdict
from datetime import datetime, timezone
from django.core.validators import RegexValidator

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
  phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
  telephone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, default="") # validators should be a list
  applications = models.ManyToManyField('Role', through='Application', related_name="role_application")

  def get_resume(self):
    skillset = defaultdict(float)
    for membership in self.member_set.all():
      # end_date = now() if membership.end_date == None else membership.end_date
      # start_date = membership.start_date
      # duration = (end_date - start_date).total_seconds() / 3600
      for period in membership.roleperiod_set.all():
        for skill in period.role.skills.all():
          skillset[skill] += period.duration()
    return [(skill, skillset[skill]) for skill in skillset]

  def apply(self, role):
    return role.apply(self.user)
  
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
class ProjectManager(models.Manager):
  def create_project(self, creator, *args, **kwargs):
    project = self.create(*args, **kwargs)
    project.set_creator(creator)
    return project

class Project(models.Model):
  channels = models.ManyToManyField('ChatChannel', through='ProjectChannel')
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=10000)
  start_date = models.DateTimeField(default=now)
  end_date = models.DateTimeField(null=True)
  active = models.BooleanField(default=True)

  objects = ProjectManager()

  def applicable_role_list(self, user):
    roles = []
    for role in self.get_roles():
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

  def add_member(self, user, roles = [], through_defaults = {}):
    through_defaults.setdefault("is_owner", False)
    through_defaults.setdefault("start_date", datetime.now(timezone.utc))
    user.profile.projects.add(self, through_defaults = through_defaults)
    membership = Member.objects.get(project=self, profile=user.profile)
    for role in roles:
      membership.roles.add(role)
    return membership

  def set_creator(self, creator):
    creator_role = Role.objects.create(project = self, title = "Creator", description = "Creator of the project.")
    self.add_member(creator, [creator_role], through_defaults = {"is_owner": True})

  def get_roles(self):
    return self.role_set.filter(active=True)

class Member(models.Model):
  profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  roles = models.ManyToManyField('Role', through='RolePeriod')
  is_owner = models.BooleanField()
  start_date = models.DateTimeField(default=now)
  end_date = models.DateTimeField(null=True)
  active = models.BooleanField(default=True)

  def deactivate(self):
    self.active = False
    self.end_date = now()
    for period in self.roleperiod_set.all():
      period.deactivate()
    self.save()

class Role(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  skills = models.ManyToManyField('Skill')
  title = models.CharField(max_length=45)
  description = models.CharField(max_length=1000)
  active = models.BooleanField(default=True)

  def __str__(self):
    return self.title

  def apply(self, user):
    if user.profile.application_set.filter(role = self).exists():
      application = user.profile.application_set.get(role = self)
      if application.status in ['R', 'D']:
        application.status = 'A'
        application.save()
        return application
      else:
        return None
    else:
      user.profile.applications.add(self, through_defaults={ "status": 'A' })
      return user.profile.application_set.get(role = self)

  def deactivate(self):
    self.active = False
    for period in self.roleperiod_set.all():
      period.deactivate()
    self.save()

class RolePeriod(models.Model):
  role = models.ForeignKey(Role, on_delete=models.CASCADE)
  membership = models.ForeignKey(Member, on_delete=models.CASCADE)
  start_date = models.DateTimeField(default=now)
  end_date = models.DateTimeField(null=True, default=None)

  def get_end(self):
    if self.end_date == None:
      return now()
    else:
      return self.end_date

  def duration(self):
    return (self.get_end() - self.start_date).total_seconds() / 3600

  def deactivate(self):
    self.end_date = now()
    self.save()

class Application(models.Model):
  applicant = models.ForeignKey(Profile, on_delete=models.CASCADE)
  role = models.ForeignKey(Role, on_delete=models.CASCADE)
  status = models.CharField(max_length=1, choices=(
    ('A', 'Applied'),
    ('O', 'Offered'),
    ('R', 'Rejected'),
    ('D', 'Declined')
  ))

  def graduate_to_membership(self):
    membership = self.role.project.add_member(self.applicant.user, [self.role])
    self.delete()
    return membership

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