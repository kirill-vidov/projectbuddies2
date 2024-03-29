from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Post, Skills, Profile


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'description', 'category', 'skillsNeeded']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'post-name'}),

        }

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'profession', 'bio', 'country', 'skills']

        widgets = {
            'bio': forms.TextInput(attrs={'type': 'textarea'}),
        }