from django.db import models
from djhago.contrib.auth.models import User

# User Data Schema
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  address = models.OneToOneField(Address, on_delete=models.CASCADE)
  projects = models.ManyToManyField(Project, through='Member')
  friends = models.ManyToManyField("self", through='Friend')
  bio = models.CharField(max_length=1000)
  telephone_number = models.DecimalField(max_digits=11)

class Address(models.Model):
  address1 = models.CharField(max_length=45)
  address2 = models.CharField(max_length=45)
  apartment_number = models.CharField(max_length=45)
  city = models.CharField(max_length=45)
  state = models.CharField(max_length=45)
  zipcode = models.CharField(max_length=45)
  country = models.CharField(max_length=45)

class Friend(models.Model):
  requestor = models.ForeignKey(Profile, on_delete=models.CASCADE)
  reciever = models.ForeignKey(Profile, on_delete=models.CASCADE)
  request_status = models.CharField(max_length=2, choices=[('RQ', 'Requested'), ('AC', 'Accepted'), ('RJ', 'Rejected')])

# Project Membership & Role Schema
class Project(models.model):
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=10000)
  startDate = models.DateField()
  endDate = models.DateField()

class Member(models.model):
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  role = models.ForeignKey(Role, on_delete=models.CASCADE)
  is_owner = models.BooleanField()
  startDate = models.DateField()
  endDate = models.DateField()

class Role(models.model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  skills = models.ManyToManyField(Skill)
  title = models.CharField(max_length=45)
  description = models.CharField(max_length=1000)

class Skill(models.model):
  parent = models.ForeignKey("self")
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=250)

# Chat Schema
