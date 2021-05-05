from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from datetime import datetime

class SignUp(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_password(self):
        paswd = "T3st_P4ssw0rd"

        resp = self.client.get("/accounts/create/", follow = True)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post("/accounts/create/", {
            "username" : "test_account",
            "first_name" : "test",
            "last_name" : "account",
            "email" : "test@account.com",
            "password1" : paswd,
            "password2" : paswd,
        }, follow = True)
        self.assertEquals(resp.status_code, 200)

        self.assertTrue(self.client.login(username = "test_account", password = paswd))

    def test_invalid_password(self):
        paswd = "abc"

        resp = self.client.get("/accounts/create/", follow = True)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post("/accounts/create/", {
            "username" : "test_account",
            "first_name" : "test",
            "last_name" : "account",
            "email" : "test@account.com",
            "password1" : paswd,
            "password2" : paswd,
        }, follow = True)
        self.assertEquals(resp.status_code, 200)

        self.assertFalse(self.client.login(username = "test_account", password = paswd))

class ProjectCreation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = "test_user", password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname')
        self.client = Client()
        self.client.login(username = self.user.username, password = "abc123")

    def test(self):
        resp = self.client.get("/project/create/", follow = True)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post("/project/create/", {
            "name" : "test_project",
            "description" : "test_project_description"
        }, follow = True)
        self.assertEquals(resp.status_code, 200)
        
        self.assertTrue(Project.objects.filter(name = "test_project").exists())

class ProfileCreation(TestCase):
    def setUp(self):
        testuser = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        
    def test_profile_creation(self):
        testuser = User.objects.get(username = 'test_user')
        self.assertNotEquals(testuser.profile, None)
        
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

