from django import forms
from .models import List, ListUser

class MugCreateForm(forms.Form):
    mug_name = forms.CharField(label="Mug Name",max_length=100)
    image_file = forms.ImageField(label="Image File")
    list = forms.ModelChoiceField(List.objects, required=True, label="Mug List")
    
    def __init__(self, *args, **kwargs):
        req_user = kwargs.pop('requesting_user')
        super().__init__(*args, **kwargs)
        self.fields['list'].queryset = List.objects.filter(id__in=ListUser.objects.filter(user=req_user).values("list"))

class ListCreateForm(forms.Form):
    list_name = forms.CharField(label="List Name",max_length=100)
    json = forms.JSONField(label="List JSON")

class LetterboxdCreateForm(forms.Form):
    letterboxd_url = forms.CharField(label="Letterboxd URL",max_length=100)

class InviteCreateForm(forms.Form):
    list = forms.ModelChoiceField(List.objects, required=True, label="Mug List")

    def __init__(self, *args, **kwargs):
        req_user = kwargs.pop('requesting_user')
        super().__init__(*args, **kwargs)
        self.fields['list'].queryset = List.objects.filter(id__in=ListUser.objects.filter(user=req_user).values("list"))