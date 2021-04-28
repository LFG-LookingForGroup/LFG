from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from datetime import datetime

class ProfileCreation(TestCase):
    def setUp(self):
        print("profile creation tests")
        testuser = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        
    def test_profile_creation(self):
        testuser = User.objects.get(username = 'test_user')
        self.assertNotEquals(testuser.profile, None)

class AnonymousAccess(TestCase):
    def setUp(self):
        print("anonymous access tests")
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
        resp = c.get(f"/accounts/profile/{testuser.id}")
        self.assertRedirects(resp, "/login/")

    def test_project_access(self):
        testproject = Project.objects.get(name="test project")
        c = Client()
        resp = c.get(f"/project/{testproject.id}")
        self.assertRedirects(resp, "/login/")

class UserAccess(TestCase):
    def setUp(self):
        print("user access tests")
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

class ProjectTestCase(TestCase):
    def setUp(self):
        print("update project tests")
        testuser = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        testproject = Project.objects.create(name= 'test_project', description='this is a testing project')
        new_role = Role.objects.create(project=testproject, title="Creator", description="Creator of the project.")
        testuser.profile.projects.add(testproject, through_defaults={"is_owner": True, "start_date": datetime.now(timezone.utc)})
        membership = testuser.profile.member_set.get(project=testproject)
        membership.roles.add(new_role)
    

    def test_update_project(self):
        testproject.name = 'edited_test_project'
        testproject.description = 'edited this is a testing project'
        
        test_project_object = Project.objects.get(name = 'test_project')
        self.assertEqual(test_project_object.name, 'edited_test_project')        
        self.assertEqual(test_project_object.description, 'edited this is a testing project')        

        