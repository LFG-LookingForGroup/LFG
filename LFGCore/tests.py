from django.test import TestCase
from LFGCore.models import Profile

# Create your tests here.
class ProjectTestCase(TestCase):
    def setup(self):
        Profile.objects.create(username = 'test_user', first_name = 'test_user_fname', last_name = 'test_user_lname', email = 'test_user@test.com')
        
