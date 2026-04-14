from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Vexillologist

# Form for creating a new user (Vexillologist) using UserCreationForm
class VexillologistCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Vexillologist
        fields = UserCreationForm.Meta.fields

class VexillologistChangeForm(forms.ModelForm):
    class Meta:
        model = Vexillologist
        fields = ('first_name', 'last_name')
