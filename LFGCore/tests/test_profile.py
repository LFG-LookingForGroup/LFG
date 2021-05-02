from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

# https://github.com/LFG-LookingForGroup/LFG/issues/5
class UpdateProfileVisibility(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.user2 = User.objects.create_user(username = 'test_user_2', password = "abc123", email = "testuser2@email.com", first_name = 'test_user_2_fname', last_name = 'test_user_2_lname',)

    def test(self):
        client = Client()
        client.login(username = self.user.username, password = "abc123")

        client2 = Client()
        client2.login(username = self.user2.username, password = "abc123")

        # update profile button appears on own profile
        resp = client.get(f"/accounts/profile/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEquals(content.select(f"form[action='/accounts/profile/update/']"), [])

        # update profile button doesn't appear on others profile
        resp = client.get(f"/accounts/profile/{self.user2.id}/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertEquals(content.select(f"form[action='/accounts/profile/update/']"), [])