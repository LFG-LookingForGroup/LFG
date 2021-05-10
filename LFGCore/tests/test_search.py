from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

# https://github.com/LFG-LookingForGroup/LFG/issues/9
class SearchResultError(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.project = Project.objects.create_project(self.user, name = 'test_project', description = 'this is a testing project')

        self.client = Client()
        self.client.login(username = self.user.username, password = "abc123")

    def test(self):
        resp = self.client.get("/search/", {"query": "test"}, follow = True)
        self.assertEquals(resp.status_code, 200)