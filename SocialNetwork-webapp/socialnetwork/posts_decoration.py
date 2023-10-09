from django import forms

from django.contrib.auth.models import User
from socialnetwork.models import Post

class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            'created_by',
            'creation_time',
            'updated_by',
            'update_time',
        )


class EditPost(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            'created_by',
            'creation_time',
            'updated_by',
        )
        widgets = {
            'update_time': forms.HiddenInput(),
        }