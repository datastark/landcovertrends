from django import forms

class InboxForm(forms.Form):
    recipient = forms.EmailField(max_length=100)
    zipfolder = forms.FileField()
