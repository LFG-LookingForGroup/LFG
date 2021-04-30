from django.test import TestCase, Client
from LFGCore.models import *
from django.contrib.auth.models import User

# https://github.com/LFG-LookingForGroup/LFG/issues/1
# https://github.com/LFG-LookingForGroup/LFG/issues/13
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