from django.conf import settings
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from user.models import User, Educator, Organisation


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


class RegistrationForm(forms.Form):
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
    username = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "UserName",
                    'type': "text"
                    }
                )
        )
    first_name = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "First Name",
                    'type': "text"
                    }
                )
        )
    last_name = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Last Name",
                    'type': "text"
                    }
                )
        )
    email = forms.EmailField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Email",
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
    password_conf = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Password Repeat",
                    'type': "password"
                    }
                )
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

