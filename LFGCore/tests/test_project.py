from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from http import HTTPStatus

# https://github.com/LFG-LookingForGroup/LFG/issues/1
# https://github.com/LFG-LookingForGroup/LFG/issues/13
class ProjectTestCases(TestCase):
    def setUp(self):
        print("update project tests")
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
        testcreator = User.objects.create(username = 'test_creator', password = "abc123", email = "testcreator@email.com", first_name = 'test_creator', last_name = 'test_creator_lname',)
        testproject = Project.objects.create(name = 'test_project', description='this is a testing project')
        testproject.set_creator(testcreator)
    
    def test(self):
        testproject = Project.objects.get(name = 'test_project')
        testcreator = User.objects.get(username = 'test_creator')
        creator_role = testcreator.profile.member_set.get(project__name = 'test_project').roles.get(title = "Creator")
        c = Client()
        c.login(username = 'test_creator', password = 'abc123')
        resp = c.get(f"/project/{testproject.id}", follow=True)
        self.assertEquals(resp.status_code, 200)
        content = BeautifulSoup(resp.content, 'html.parser')
        self.assertEquals(len(content.select(f"form[action='/role/apply/{creator_role.id}/']")), 0)
