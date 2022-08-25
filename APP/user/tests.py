from django.conf import settings
from django.test import TestCase
from user.model import User
from user.views import _loginUser, _registerUser, \
        _activate, _logoutUser
from .util.GeneralUtil import account_activation_token, password_reset_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str


# User creation tests
class User_creation_Tests(TestCase):
    def setUp(self):
        self.User = User
        self.first = 'mustafa'
        self.last = 'omar'
        self.user_name = 'user'
        self.email = 'mustafa12211@hotmail.co.uk'
        self.password = '123'
        self.password_conf = '123'
        self.data = {
                'usertype': 'Student',
                'firstname': self.first,
                'lastname': self.last,
                'username': self.user_name,
                'email': self.email,
                'password': self.password,
                'password_conf': self.password_conf,
            }
        self.login_data = {
                'username': self.user_name,
                'password': self.password
            }
        self.pwdreset_data = {
                'uidb64': '',
                'token': '',
                'password': '12345',
                'password_conf': '12345'
            }

    def test_user_register(self):
        response = self.client.post('/user/_registerUser', self.data)
        # The response should be a redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login")
        # The user should be present in the database
        existance = self.User.objects.filter(
                username__iexact=self.user_name
            ).exists()
        self.assertEqual(existance, True)
        # The user should not be able to login util confirmation
        login_res = self.client.post('/user/_login', self.login_data)
        # Fail to login directly after registration
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, "/user/login")

    def test_user_register_types(self):
        # Create each user group type and check that they pass
        for user_group in settings.VALID_GROUPS:
            self.data['usertype'] = user_group
            # Test all different types of users and their group assignments
            self.test_user_register()
            user = self.User.objects.get(
                    username__iexact=self.user_name
                )
            group = user.groups.get()
            self.assertEqual(user_group, str(group))
            user.delete()

    def test_user_login(self):
        # register user but dont check for that here
        # there should be another test for that
        self.test_user_register()
        user = User.objects.get(username__iexact=self.user_name)
        # The user should click the confirmation email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_res = self.client.get(
                '/user/_activate/'+uid+'/'+token
            )
        #
        login_res = self.client.post('/user/_login', self.login_data)
        # Registration should be successful an sends you to login page
        self.assertEqual(activation_res.status_code, 302)
        self.assertEqual(activation_res.url, '/user/login')
        # Response should be a redirect to the index
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, "/user/")

    def test_user_logout(self):
        # register user but dont check for that here
        # there should be another test for that
        self.test_user_login()
        logout_res = self.client.post('/user/_logout')
        self.assertEqual(logout_res.status_code, 302)
        self.assertEqual(logout_res.url, "/")

    def test_user_password_change(self):
        # register and get user
        self.test_user_logout()
        user = User.objects.get(username__iexact=self.user_name)
        # get encrypted id and token
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)
        # check access to password reset page
        pwdreset_page_result = self.client.get(
                '/user/pwdreset/'+uidb64+'/'+token
            )
        self.assertEqual(pwdreset_page_result.status_code, 200)
        # check password reset functionality
        self.pwdreset_data['uidb64'] = uidb64
        self.pwdreset_data['token'] = token
        pwd_reset_result = self.client.post(
                '/user/_pwdreset',
                self.pwdreset_data
            )
        self.assertEqual(pwd_reset_result.status_code, 302)
        self.assertEqual(pwd_reset_result.url, '/user/login')
        # check password changed
        oldpass_login = False
        try:
            self.test_user_logout()
        except Exception:
            pass
        else:
            oldpass_login = True
        #
        newpass_login = True
        try:
            self.data['password'] = self.pwdreset_data['password']
            self.data['password_conf'] = self.pwdreset_data['password']
            self.login_data['password'] = self.pwdreset_data['password']
            self.test_user_logout()
        except Exception:
            pass
        else:
            newpass_login = True
        self.assertEqual(oldpass_login, False)
        self.assertEqual(newpass_login, True)

# Url tests
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
