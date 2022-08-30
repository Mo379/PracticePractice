from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
            label='username',
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Username/Email",
                    'type': "text"
                    }
                )
        )
    password = forms.CharField(
            label='password',
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
            label='username',
            max_length=200,
            widget=forms.TextInput(attrs={
                    'class': "form-control form-control-user",
                    'placeholder': "Username/Email",
                    'type': "text"
                    }
                )
        )
