from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_registration.forms import User


class RegistrationForm(UserCreationForm):
    submit_button = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'submit', 'value': 'Registrovat', 'class': 'button'}),
        label=''  # Nastavení label na prázdný řetězec
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def render_submit_button(self):
        # Tato funkce vytvoří HTML kód pro tlačítko Registrovat
        return str(self['submit_button'])


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)
