from django.test import TestCase
from user.models import User


# Create your tests here.
class URL_pages_Tests(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='superuser', password='secret', email='admin@example.com'
        )
        self.client.login(username='superuser', password='secret')

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_my(self):
        response = self.client.get('/my/')
        self.assertEqual(response.status_code, 200)

    def test_user(self):
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, 200)

    def test_student_dash(self):
        response = self.client.get('/s-dash/')
        self.assertEqual(response.status_code, 200)

    def test_admin(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
