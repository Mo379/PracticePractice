from django import forms 

class LoginForm(froms.Form):
    email = forms.CharField(label='Email', max_length=100)
    password= forms.CharField(label='Password', max_length=100)
