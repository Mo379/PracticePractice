from django.test import TestCase

# Create your tests here.
class URL_pages_Tests(TestCase):
    def test_homepage(self):
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, 200)
    def test_login(self):
        response = self.client.get('/user/login')
        self.assertEqual(response.status_code, 200)
    def test_register(self):
        response = self.client.get('/user/register')
        self.assertEqual(response.status_code, 200)
    def test_forgotpassword(self):
        response = self.client.get('/user/forgotpassword')
        self.assertEqual(response.status_code, 200)
    def test_billing(self):
        response = self.client.get('/user/billing')
        self.assertEqual(response.status_code, 200)
    def test_security(self):
        response = self.client.get('/user/security')
        self.assertEqual(response.status_code, 200)
    def test_settings(self):
        response = self.client.get('/user/settings')
        self.assertEqual(response.status_code, 200)
    def test_join(self):
        response = self.client.get('/user/join')
        self.assertEqual(response.status_code, 200)
