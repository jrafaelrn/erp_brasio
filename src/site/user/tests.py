from django.test import TestCase
from .models import User

class UserTestCase(TestCase):
    
    def setUp(self):
        User.objects.create(username="test", password="test", email="")

    def test_user(self):
        print("Testing user...")
        user = User.objects.get(username="test")
        self.assertEqual(user.username, "test")
        self.assertEqual(user.password, "test")
        self.assertEqual(user.email, "")