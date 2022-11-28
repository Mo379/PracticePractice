import re
from datetime import datetime
from django.conf import settings
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from user.models import (
        User
    )
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from user.util.GeneralUtil import \
        account_activation_token, password_reset_token


alphanumeric = RegexValidator(
        r'^[0-9a-zA-Z]*$',
        'Only alphanumeric characters are allowed.'
    )


class LoginForm(forms.Form):
    username = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Username/Email",
                    'type': "text"
                    }
                )
        )
    password = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Password",
                    'type': "password"
                    }
                )
        )

    # checking if user exits
    def clean_username(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        try:
            user = User.objects.get(email__iexact=username)
        except Exception:
            try:
                user = User.objects.get(username__iexact=username)
            except Exception:
                raise ValidationError(
                        "User does not exist."
                    )
        # checking if user is registered
        if user.registration == False and user.is_superuser == False:
            raise ValidationError(
                    "Incomplete Registration."
                )
        # checking if the user is in the password reset state
        if user.password_set== False and user.is_superuser == False:
            raise ValidationError(
                    "Incomplete Password Reset Sequence."
                )
        return user.username


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Username/Email",
                    'type': "text"
                    }
                )
        )

    # checking if user exists
    #     check email
    #     check username
    # admins cannot do this
    # Activating the password reset sequence
    def clean_username(self):
        cleaned_data = super().clean()
        username = cleaned_data['username']
        try:
            user = User.objects.get(email__iexact=username)
        except Exception:
            try:
                user = User.objects.get(username__iexact=username)
            except Exception:
                raise ValidationError(
                        "User does not exist."
                    )
        if user.is_superuser:
            raise ValidationError(
                    "Action is invalid for this user."
                )
        user.password_set = False
        user.save()
        return user.username


class RegistrationForm(forms.ModelForm):
    password_conf = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Password Repeat",
                    'type': "password"
                    }
                )
        )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
                'username': 'User Name',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'Email',
                'password': 'Password',
            }
        widgets = {
                'username': forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "UserName",
                    'type': "text"
                    }
                ),
                'first_name': forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "First Name",
                    'type': "text"
                    }
                ),
                'last_name': forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Last Name",
                    'type': "text"
                    }
                ),
                'email': forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Email",
                    'type': "text"
                    }
                ),
                'password': forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Password",
                    'type': "password"
                    }
                ),
            }

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_conf = cleaned_data.get('password_conf')
        if password != password_conf:
            self.add_error(
                    'password', ValidationError('Passwords do not match.')
                )
        #
        username_c = User.objects.filter(username__iexact=username).exists()
        email_c = User.objects.filter(email__iexact=email).exists()
        if username_c:
            self.add_error(
                    'username',
                    ValidationError('An account with this username ' +
                    'already exists, please try again')
                )
        if email_c:
            self.add_error(
                    'email',
                    ValidationError('An account with this email ' +
                    'already exists, please try again')
                )


class ResetPasswordForm(forms.Form):
    def __init__(self, uidb64, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uidb64'] = forms.CharField(
            max_length=50,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "",
                    'type': "hidden",
                    'value': uidb64
                    }
                )
            )
        self.fields['token'] = forms.CharField(
                max_length=50,
                widget=forms.TextInput(attrs={
                        'class': "form-control form-control-user",
                        'placeholder': "",
                        'type': "hidden",
                        'value': token
                        }
                    )
            )

    password_new = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "New Password",
                    'type': "password"
                    }
                )
        )
    password_conf = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "New Password Repeat",
                    'type': "password"
                    }
                )
        )
    uidb64 = forms.CharField()
    token = forms.CharField()

    # check confirmation password match
    # password length
    # get user id from uidb64 and create user
    # check super user they cannot do this
    # check token with user
    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        try:
            uid = force_str(urlsafe_base64_decode(cleaned_data['uidb64']))
            user = User.objects.get(pk=uid)
            cleaned_data['uidb64'] = uid
            if user.is_superuser:
                self.add_error(
                        'uidb64',
                        ValidationError('Action is invalid for this user.')
                    )
            if password_reset_token.check_token(user, cleaned_data['token']) \
                    == False:
                self.add_error(
                        'token',
                        ValidationError('Invalid token.')
                    )
        except Exception:
            self.add_error(
                    'uidb64',
                    ValidationError('Invalid Information.')
                )
        if cleaned_data['password_new'] != cleaned_data['password_conf']:
            self.add_error(
                    'password_new',
                    ValidationError('Passwords do not match.')
                )


class ChangePasswordForm(forms.Form):
    password_current = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Curren Password",
                    'type': "password"
                    }
                )
        )
    password_new = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "New Password",
                    'type': "password"
                    }
                )
        )
    password_conf = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "New Password Repeat",
                    'type': "password"
                    }
                )
        )

    # new and conf pass checks
    # old and new pass checks
    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password_old = cleaned_data['password_current']
        password_new = cleaned_data['password_new']
        password_conf = cleaned_data['password_conf']
        if password_old == password_new:
            self.add_error(
                    'password_current',
                    ValidationError('Current and New ' +
                    'Passwords cannot be the same.')
                )
        if password_conf != password_new:
            self.add_error(
                    'password_new',
                    ValidationError('New and Confirmation ' +
                    'Passwords do not match.')
                )


class TriggerDeleteAccountForm(forms.Form):
    password = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Password",
                    'type': "password"
                    }
                )
        )


class DeleteAccountForm(forms.Form):
    def __init__(self, uidb64, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uidb64'] = forms.CharField(
            max_length=50,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "",
                    'type': "hidden",
                    'value': uidb64
                    }
                )
            )
        self.fields['token'] = forms.CharField(
                max_length=50,
                widget=forms.TextInput(attrs={
                        'class': "form-control form-control-user",
                        'placeholder': "",
                        'type': "hidden",
                        'value': token
                        }
                    )
            )
    uidb64 = forms.CharField()
    token = forms.CharField()
    username = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Username/Email",
                    'type': "text"
                    }
                )
        )
    password = forms.CharField(
            max_length=20,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Password",
                    'type': "password"
                    }
                )
        )

    def clean(self):
        cleaned_data = super(DeleteAccountForm, self).clean()
        # check url information
        try:
            uid = force_str(urlsafe_base64_decode(cleaned_data['uidb64']))
            user = User.objects.get(pk=uid)
            cleaned_data['uidb64'] = uid
            if user.is_superuser:
                self.add_error(
                        'uidb64',
                        ValidationError('Action is invalid for this user.')
                    )
            if account_activation_token.check_token(
                    user, cleaned_data['token']
                    ) == False:
                self.add_error(
                        'token',
                        ValidationError('Invalid token.')
                    )
        except Exception:
            self.add_error(
                    'uidb64',
                    ValidationError('Invalid Information.')
                )
        username = cleaned_data.get('username')
        try:
            user = User.objects.get(email__iexact=username)
        except Exception:
            try:
                user = User.objects.get(username__iexact=username)
            except Exception:
                self.add_error(
                        'username',
                        ValidationError("User does not exist.")
                    )
        if user.registration == False and user.is_superuser == False:
                self.add_error(
                        'username',
                        ValidationError("Incomplete registration.")
                    )
        # checking if the user is in the password reset state
        if user.password_set== False and user.is_superuser == False:
                self.add_error(
                        'username',
                        ValidationError("Incomplete password reset sequence.")
                    )
        cleaned_data['username'] = user.username


class EmailChoiceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['mail_choices']
        labels = {
                'mail_choices': 'Choose which types of email \
                        updates you receive'
            }
        widgets = {
            "mail_choices": forms.CheckboxSelectMultiple(attrs={
                        'class': "",
                        'placeholder': "Mail choices",
                        'type': "checkbox",
                    }
                )
            }

    def clean_mail_choices(self):
        cleaned_data = super(EmailChoiceForm, self).clean()
        mail_choices = cleaned_data['mail_choices']
        if 'Core' not in mail_choices:
            mail_choices.append('Core')
        return mail_choices


class AppearanceChoiceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['theme']
        labels = {
                'theme': 'Select your color scheme'
            }
        widgets = {
            "theme": forms.RadioSelect(attrs={
                        'class': "",
                        'placeholder': "Theme choices",
                        'type': "radio",
                    }
                )
            }


class LanguageChoiceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['language']
        labels = {
                'language': 'Select your preferred language'
            }
        widgets = {
            "language": forms.RadioSelect(attrs={
                        'class': "",
                        'placeholder': "Language choices",
                        'type': "radio",
                    }
                )
            }


class AccountDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                'profile_upload',
                'username',
                'first_name',
                'last_name',
                'email',
                'date_of_birth',
                'bio'
            ]
        labels = {
                'profile_upload': 'Profile Picture: (A clear face shot with white background to be professional)',
                'username': 'Username (This is only a key used for loggin in, no other user will see this.)',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'Email',
                'date of birth': 'Date Of Birth (D-M-Y)',
                'bio': 'Biography',
            }
        widgets = {
            'profile_upload': forms.FileInput(),
            "username": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Username",
                        'type': "text",
                    }
                ),
            "first_name": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "First Name",
                        'type': "text",
                    }
                ),
            "last_name": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Last Name",
                        'type': "text",
                    }
                ),
            "email": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Email",
                        'type': "text",
                    }
                ),
            "date_of_birth": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Date Of Birth",
                        'type': "date",
                    }
                ),
            "bio": forms.Textarea(attrs={
                        'class': "form-control",
                        'placeholder': "Tell use a bit about yourself. (Academically, Aspirationally)",
                        'type': "textarea",
                    }
                ),
            }

    def clean(self):
        cleaned_data = super(AccountDetailsForm, self).clean()
        username = cleaned_data['username']
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        email = cleaned_data['email']
        date_of_birth = cleaned_data['date_of_birth']
        bio = cleaned_data['bio']
        #
        if re.match(r'^[A-Za-z0-9_]+$', username) is None:
            self.add_error(
                'username',
                ValidationError(
                    "Invalid username, you're allowed alphanumeric characters " +
                    "with underscores only, please try again."
                )
            )
        # first name check
        if re.match(r'^[A-Za-z]+$', first_name) is None:
            self.add_error(
                'first_name',
                ValidationError(
                    "Invalid name, you're allowed alphabetical " +
                    "characters only, please try again."
                )
            )
        # last name check
        if re.match(r'^[A-Za-z]+$', last_name) is None:
            self.add_error(
                'last_name',
                ValidationError(
                    "Invalid name, you're allowed alphabetical " +
                    "characters only, please try again."
                )
            )
        # dob check
        try:
            datetime.strptime(str(date_of_birth), '%Y-%m-%d')
        except Exception:
            self.add_error(
                'date_of_birth',
                ValidationError(
                    "The entered date of birth is invalid, " +
                    "please try again."
                )
            )
        # bio check
        if len(bio) > 500 or len(bio) < 25 or re.match(r'^[A-Za-z0-9_.,]+$', bio):
            self.add_error(
                'bio',
                ValidationError(
                    'Your Bio is invalid, youre allowed ' +
                    'alphanumeric and the following (_.,) characters'
                )
            )


