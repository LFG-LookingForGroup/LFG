from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User

class ProfileCreation(TestCase):
    def setUp(self):
        print("profile creation tests")
        testuser = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        
    def test_profile_creation(self):
        testuser = User.objects.get(username = 'test_user')
        self.assertNotEquals(testuser.profile, None)