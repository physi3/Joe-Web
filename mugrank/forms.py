from django import forms
from .models import List

class MugCreateForm(forms.Form):
    mug_name = forms.CharField(label="Mug Name",max_length=100)
    image_file = forms.ImageField(label="Image File")
    list = forms.ModelChoiceField(List.objects, required=True, label="Mug List")
    