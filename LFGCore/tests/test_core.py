from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from datetime import datetime

class AnonymousAccess(TestCase):
    def setUp(self):
        User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        Project.objects.create(name = "test project", description = "this is a test project")

    def test_landing_access(self):
        c = Client()
        resp = c.get("/", follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_about_access(self):
        c = Client()
        resp = c.get("/about/", follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_search_access(self):
        c = Client()
        resp = c.get("/search/", follow=True)
        self.assertEquals(resp.status_code, 200)
    
    def test_profile_access(self):
        testuser = User.objects.get(username="test_user")
        c = Client()
        url = f"/accounts/profile/{testuser.id}/"
        resp = c.get(url, follow=True)
        self.assertRedirects(resp, f"/login/?next={url}")

    def test_project_access(self):
        testproject = Project.objects.get(name="test project")
        c = Client()
        url = f"/project/{testproject.id}/"
        resp = c.get(url, follow=True)
        self.assertRedirects(resp, f"/login/?next={url}")

class UserAccess(TestCase):
    def setUp(self):
        testuser = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        testproject = Project.objects.create(name = "test project", description = "this is a test project")
        testuser.profile.projects.add(testproject, through_defaults={"is_owner": True, "start_date" : datetime.now(timezone.utc)})
        
    def test_landing_access(self):
        c = Client()
        c.login(username = "test_user", password = "abc123")
        resp = c.get("/", follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_about_access(self):
        c = Client()
        c.login(username = "test_user", password = "abc123")
        resp = c.get("/about/", follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_search_access(self):
        c = Client()
        c.login(username = "test_user", password = "abc123")
        resp = c.get("/search/", follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_profile_access(self):
        testuser = User.objects.get(username="test_user")
        c = Client()
        c.login(username = "test_user", password = "abc123")
        resp = c.get(f"/accounts/profile/{testuser.id}", follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_project_access(self):
        testproject = Project.objects.get(name="test project")
        c = Client()
        c.login(username = "test_user", password = "abc123")
        resp = c.get(f"/project/{testproject.id}", follow=True)
        self.assertEquals(resp.status_code, 200)
