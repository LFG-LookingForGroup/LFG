from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from datetime import datetime
from bs4 import BeautifulSoup

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

class RoleCreation(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        self.project = Project.objects.create_project(self.creator, name = 'test_project', description = 'this is a testing project')
        self.skill1 = Skill.objects.create(name = "test_skill_1", description = "this is a test skill")
        self.skill2 = Skill.objects.create(name = "test_skill_2", description = "this is another test skill")
        self.client = Client()
        self.client.login(username = self.creator.username, password = "abc123")
    
    def test_create_single_skill_role(self):
        resp = self.client.get(f"/project/{self.project.id}/", follow = True)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post("/role/create/", {
            "title" : "test_role",
            "description" : "this is a test role",
            "skills" : self.skill1.id,
            "project" : self.project.id
        }, follow = True)
        self.assertTrue(resp.status_code, 200)

        role_query = Role.objects.filter(title = "test_role", project = self.project)
        self.assertTrue(role_query.exists())

        role = role_query.first()
        self.assertTrue(self.skill1 in role.skills.all())

    def test_create_multi_skill_role(self):
        resp = self.client.get(f"/project/{self.project.id}/", follow = True)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post("/role/create/", {
            "title" : "test_role",
            "description" : "this is a test role",
            "skills" : [self.skill1.id, self.skill2.id],
            "project" : self.project.id
        }, follow = True)
        self.assertTrue(resp.status_code, 200)

        role_query = Role.objects.filter(title = "test_role", project = self.project)
        self.assertTrue(role_query.exists())

        role = role_query.first()
        self.assertTrue(self.skill1 in role.skills.all())
        self.assertTrue(self.skill2 in role.skills.all())

class ProfileCreation(TestCase):
    def setUp(self):
        testuser = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        
    def test_profile_creation(self):
        testuser = User.objects.get(username = 'test_user')
        self.assertNotEquals(testuser.profile, None)

class Search(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        self.project = Project.objects.create_project(self.creator, name = 'test_project', description = 'this is a testing project')
        self.skill1 = Skill.objects.create(name = "test_skill_1", description = "this is a test skill")
        self.skill2 = Skill.objects.create(name = "test_skill_2", description = "this is another test skill")
        self.client = Client()
        self.client.login(username = self.creator.username, password = "abc123")

    def test_basic_search(self):
        resp = self.client.get("/search/", {
            "query": "test"
        }, follow = True)
        content = BeautifulSoup(resp, "html.parser")
        self.assertNotEqual(content.select(f"a[href='/project/{self.project.id}/']"), [])

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

