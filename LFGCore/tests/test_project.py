from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

# https://github.com/LFG-LookingForGroup/LFG/issues/1
# https://github.com/LFG-LookingForGroup/LFG/issues/13
class ProjectTestCase(TestCase):
    def setUp(self):
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


# https://github.com/LFG-LookingForGroup/LFG/issues/2
class ApplyForRoleAsCreator(TestCase):
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
