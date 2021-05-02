from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

# https://github.com/LFG-LookingForGroup/LFG/issues/5
class UpdateProfileButtonVisibility(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.user2 = User.objects.create_user(username = 'test_user_2', password = "abc123", email = "testuser2@email.com", first_name = 'test_user_2_fname', last_name = 'test_user_2_lname',)
        
        self.client = Client()
        self.client.login(username = self.user.username, password = "abc123")

    def test_appears_on_own_profile(self):
        resp = self.client.get(f"/accounts/profile/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEquals(content.select(f"form[action='/accounts/profile/update/']"), [])

    def test_appears_on_own_profile_explicit_link(self):
        resp = self.client.get(f"/accounts/profile/{self.user.id}/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEquals(content.select(f"form[action='/accounts/profile/update/']"), [])

    def test_doesnt_appear_on_other_profile(self):
        resp = self.client.get(f"/accounts/profile/{self.user2.id}/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertEquals(content.select(f"form[action='/accounts/profile/update/']"), [])

# https://github.com/LFG-LookingForGroup/LFG/issues/12
class PasswordUpdateRequirementsSatisfied(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
    
        self.client = Client()
        self.client.login(username = self.user.username, password = "abc123")

    def test_incorrect_password_change(self):
        resp = self.client.post("/accounts/profile/update/", {
            'update-type' : 'password',
            'old_password' : 'abc123',
            'new_password1' : '1',
            'new_password2' : '1'
        })
        self.assertFalse(self.client.login(username = self.user.username, password = '1'))

    def test_correct_password_change(self):
        resp = self.client.post("/accounts/profile/update/", {
            'update-type' : 'password',
            'old_password' : 'abc123',
            'new_password1' : 'Tr0ub4dor&3',
            'new_password2' : 'Tr0ub4dor&3'
        })
        self.assertTrue(self.client.login(username = self.user.username, password = 'Tr0ub4dor&3'))

# https://github.com/LFG-LookingForGroup/LFG/issues/16
class ProfileUpdateRequiredFields(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
    
        self.client = Client()
        self.client.login(username = self.user.username, password = "abc123")

    def test(self):
        resp = self.client.get("/accounts/profile/update/", follow = True)
        self.assertEquals(resp.status_code, 200)

        content = BeautifulSoup(resp.content, "html.parser")
        self.assertTrue(content.select_one("#id_username").has_attr("required"))
        self.assertTrue(content.select_one("#id_first_name").has_attr("required"))
        self.assertTrue(content.select_one("#id_last_name").has_attr("required"))
        self.assertTrue(content.select_one("#id_email").has_attr("required"))

# https://github.com/LFG-LookingForGroup/LFG/issues/21
class LeaveProjectButtonOnOtherProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'test_user', password = "abc123", email = "testuser@email.com", first_name = 'test_user_fname', last_name = 'test_user_lname',)
        self.creator = User.objects.create_user(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        self.project = Project.objects.create(name = 'test_project', description = 'this is a testing project')
        self.creator_membership = self.project.set_creator(self.creator)

    def test_appears_on_own_profile(self):
        client = Client()
        client.login(username = self.creator.username, password = 'abc123')

        resp = client.get(f"/accounts/profile/{self.creator.id}/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertNotEqual(content.select(f"form[action='/membership/quit/{self.creator_membership.id}/']"), [])

    def test_doesnt_appear_on_other_profile(self):
        client = Client()
        client.login(username = self.user.username, password = 'abc123')

        resp = client.get(f"/accounts/profile/{self.creator.id}/", follow = True)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertEqual(content.select(f"form[action='/membership/quit/{self.creator_membership.id}/']"), [])
