from django import forms

from .models import Recenze


class Recenzedit(forms.ModelForm):
    class Meta:
        model = Recenze
        fields = ('text',)
