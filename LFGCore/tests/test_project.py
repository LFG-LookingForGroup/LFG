from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from http import HTTPStatus
from datetime import timedelta

# https://github.com/LFG-LookingForGroup/LFG/issues/1
# https://github.com/LFG-LookingForGroup/LFG/issues/13
class ProjectTestCases(TestCase):
    def setUp(self):
        #Create User
        self.user = User.objects.create(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        #Create project
        test_project = Project.objects.create(name= 'test_project', description='this is a testing project')
        test_project.set_creator(self.user)
    

    def test_update_project(self):
        c = Client()
        test_project = Project.objects.get(id=1)
        orig_name = test_project.name
        orig_description = test_project.description
        
        response = c.post(
            f"/project/update/{test_project.id}", {"name": "a new test_project", "description": "a new testing project description"}, follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(orig_name, test_project.name)
        self.assertEqual(orig_description, test_project.description)


# https://github.com/LFG-LookingForGroup/LFG/issues/2
class ApplyForCreatorRoleAsCreator(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.creator = User.objects.create_user(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        self.project = Project.objects.create(name = 'test_project', description='this is a testing project')
        self.project.set_creator(self.creator)
        self.creator_role = self.creator.profile.member_set.get(project__name = 'test_project').roles.get(title = "Creator")
    
    def test_present_as_user(self):
        c = Client()
        c.login(username = 'test_user', password = "abc123")
        resp = c.get(f"/project/{self.project.id}/", follow=True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEquals(content.select(f"form[action='/role/apply/{self.creator_role.id}/']"), [])

    def test_not_present_as_creator(self):
        c = Client()
        c.login(username = 'test_creator', password = "abc123")
        resp = c.get(f"/project/{self.project.id}/", follow=True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertEquals(content.select(f"form[action='/role/apply/{self.creator_role.id}/']"), [])

# https://github.com/LFG-LookingForGroup/LFG/issues/3
class ReapplyAfterDecline(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.creator = User.objects.create_user(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        self.project = Project.objects.create(name = 'test_project', description='this is a testing project')
        self.project.set_creator(self.creator)
        self.creator_role = self.creator.profile.member_set.get(project = self.project).roles.get(title = "Creator")
        self.skill = Skill.objects.create(name = "test_skill", description = "this is a test skill")
        self.role = Role.objects.create(title = "test_role", description = "test role description", project = self.project)
        self.role.skills.add(self.skill)

    def test(self):
        user_client = Client()
        user_client.login(username = 'test_user', password = 'abc123')

        creator_client = Client()
        creator_client.login(username = 'test_creator', password = 'abc123')

        # apply for role
        user_client.post(f"/role/apply/{self.role.id}/", {"redirect" : f"/project/{self.project.id}/"}, follow=True)
        application = self.user.profile.application_set.filter(role = self.role, status='A')
        self.assertTrue(application.exists())
        application = application.first()

        # present offer
        creator_client.post(f"/application/updatestatus/{application.id}/", {"newstatus" : "O"}, follow=True)
        self.assertEquals(self.user.profile.application_set.get(role = self.role).status, "O")

        # decline offer
        user_client.post(f"/application/updatestatus/{application.id}/", {"newstatus" : "D"}, follow=True)
        self.assertEquals(self.user.profile.application_set.get(role = self.role).status, "D")

        # check if role is applicable
        resp = user_client.get(f"/project/{self.project.id}/", follow=True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEquals(content.select(f"form[action='/role/apply/{self.role.id}/']"), [])

# https://github.com/LFG-LookingForGroup/LFG/issues/4
class MaintainSkillAfterQuit(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.creator = User.objects.create_user(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        self.project = Project.objects.create(name = 'test_project', description='this is a testing project')
        self.project.set_creator(self.creator)
        self.creator_role = self.creator.profile.member_set.get(project = self.project).roles.get(title = "Creator")
        self.skill = Skill.objects.create(name = "test_skill", description = "this is a test skill")
        self.role = Role.objects.create(title = "test_role", description = "test role description", project = self.project)
        self.role.skills.add(self.skill)

    def test(self):
        user_client = Client()
        user_client.login(username = "test_user", password = "abc123")

        creator_client = Client()
        creator_client.login(username = 'test_creator', password = 'abc123')

        # apply for role
        user_client.post(f"/role/apply/{self.role.id}/", {"redirect" : f"/project/{self.project.id}/"}, follow=True)
        application = self.user.profile.application_set.filter(role = self.role, status='A')
        self.assertTrue(application.exists())
        application = application.first()

        # present offer
        creator_client.post(f"/application/updatestatus/{application.id}/", {"newstatus" : "O"}, follow=True)
        self.assertEquals(self.user.profile.application_set.get(role = self.role).status, "O")

        # accept offer
        user_client.post(f"/project/acceptoffer/{application.id}/", follow=True)
        membership = self.user.profile.member_set.filter(project = self.project)
        self.assertTrue(membership.exists())
        membership = membership.first()
        self.assertTrue(membership.active)

        # set experience to be 1 hour
        membership.start_date -= timedelta(hours=1)
        membership.save()
        
        # check that experience is recorded
        resume = self.user.profile.get_resume()
        self.assertGreater(len(resume), 0)
        self.assertEqual(resume[0][0], self.skill)
        self.assertGreaterEqual(resume[0][1], 1)

        # quit position
        user_client.post(f"/membership/quit/{membership.id}/", follow=True)
        self.assertFalse(self.user.profile.member_set.get(project = self.project).active)

        # check that experience remains recorded
        resume = self.user.profile.get_resume()
        self.assertGreater(len(resume), 0)
        self.assertEqual(resume[0][0], self.skill)
        self.assertGreaterEqual(resume[0][1], 1)

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
        resp = client.get(f"/accounts/profile/", follow=True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEquals(content.select(f"form[action='/accounts/profile/update/']"), [])

        # update profile button doesn't appear on others profile
        resp = client.get(f"/accounts/profile/{self.user2.id}/", follow=True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertEquals(content.select(f"form[action='/accounts/profile/update/']"), [])