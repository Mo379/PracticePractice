from django.conf import settings
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from user.models import User, Educator, Organisation
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator


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


class RegistrationForm(forms.ModelForm):
    CHOICES = []
    for choice in settings.VALID_GROUPS:
        CHOICES.append((choice, choice))
    usertype = forms.ChoiceField(
            choices=BLANK_CHOICE_DASH+CHOICES,
            label='Please select a string',
            required=True,
            widget=forms.Select(attrs={
                    'class': "form-select",
                    'style': "width:100%;padding:10px;\
                            border-radius:10rem 5rem 5rem 10rem;",
                    'placeholder': "Username/Email",
                    'type': "text"
                    }
                )
        )
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
            self.add_error('password', 'Passwords do not match.')
        #
        username_c = User.objects.filter(username__iexact=username).exists()
        email_c = User.objects.filter(email__iexact=email).exists()
        if username_c:
            self.add_error(
                    'username',
                    'An account with this username ' +
                    'already exists, please try again'
                )
        if email_c:
            self.add_error(
                    'email',
                    'An account with this email ' +
                    'already exists, please try again'
                )

class ResetPasswordForm(forms.Form):
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
                'username',
                'first_name',
                'last_name',
                'email',
                'date_of_birth',
                'bio'
            ]
        labels = {
                'username': 'Username (how your name will appear to other users on the site)',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'Email',
                'date of birth': 'Date Of Birth (D-M-Y)',
                'bio': 'Biography',
            }
        widgets = {
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


class OrganisationDetailsForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['name', 'phone_number', 'incorporation_date', 'url', 'location']
        labels = {
                'name': 'Organisation Name',
                'phone_number': 'Phone Number',
                'incorporation_date': 'Incorporation Date',
                'url': 'Organisation URL',
                'location': 'Organisation Physical Location. (Building number, road, town, city, postcode, country)',
            }
        widgets = {
            "name": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Organisation's Name",
                        'type': "text",
                    }
                ),
            "phone_number": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Organisation's Phone Number",
                        'type': "text",
                    }
                ),
            "incorporation_date": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Organisation's Incorporation Date",
                        'type': "text",
                    }
                ),
            "url": forms.TextInput(attrs={
                        'class': "form-control",
                        'placeholder': "Organisation's URL",
                        'type': "text",
                    }
                ),
            "location": forms.Textarea(attrs={
                        'class': "form-control",
                        'placeholder': "Organisation's Physical Location.",
                        'type': "textarea",
                    }
                )
            }

