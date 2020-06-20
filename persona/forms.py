from django import forms
from django.contrib.auth.models import User
from . import models
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

def check_email(value):
    users = User.objects.all()
    for user in users:
        if user.email == value:
            raise ValidationError("This email is already taken by another account.");

class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text="Please, Enter a Valid Email!", max_length=100, validators=[check_email])
    first_name = forms.CharField(help_text="Required. 20 characters or fewer.", max_length=20)
    last_name = forms.CharField(help_text="Required. 20 characters or fewer.", max_length=20)
    username = forms.CharField(help_text="Required. 20 characters or fewer.", max_length=20)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'some-space'})
        self.fields['last_name'].widget.attrs.update({'class': 'some-space'})
        self.fields['email'].widget.attrs.update({'class': 'some-space'})
        self.fields['password1'].widget.attrs.update({'class': 'some-space'})

    #

class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ('dp', 'dob', 'bio')
        labels = {
            "dp": "Profile picture",
            "dob": "Date of birth",
            "bio": "Bio",
        }
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['dp'].widget.attrs.update({'class': 'form_dp'})
        self.fields['dob'].widget.attrs.update({'class': 'form_dob'})
        self.fields['bio'].widget.attrs.update({'class': 'form_bio'})

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(help_text="Please, Enter a Valid Email!", max_length=100)
    first_name = forms.CharField(help_text="Required. 20 characters or fewer.", max_length=20)
    last_name = forms.CharField(help_text="Required. 20 characters or fewer.", max_length=20)
    username = forms.CharField(help_text="Required. 20 characters or fewer.", max_length=20)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form_username'})
        self.fields['first_name'].widget.attrs.update({'class': 'form_fname'})
        self.fields['last_name'].widget.attrs.update({'class': 'form_lname'})
        self.fields['email'].widget.attrs.update({'class': 'form_email'})

class TextForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('txt', 'tags')
        labels = {
            "txt": "Write Here",
            "tags": "Tags",
        }
    def __init__(self, *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        self.fields['txt'].widget.attrs.update({'class': 'form_txt'})

class ImageForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('img', 'dst', 'tags')
        labels = {
            "img": "Upload image",
            "dst": "Description",
            "tags": "Tags",
        }
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['dst'].widget.attrs.update({'class': 'form_dst'})

class VideoForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('title', 'vid', 'dst', 'tags')
        labels = {
            "title": "Title",
            "vid": "Upload Video",
            "dst": "Description",
            "tags": "Tags",
        }
    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        self.fields['dst'].widget.attrs.update({'class': 'form_dst'})
        self.fields['title'].widget.attrs.update({'class': 'form_title'});

class AudioForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('title', 'aud', 'dst', 'tags')
        labels = {
            "title": "Title",
            "aud": "Upload Audio",
            "dst": "Description",
            "tags": "Tags",
        }
    def __init__(self, *args, **kwargs):
        super(AudioForm, self).__init__(*args, **kwargs)
        self.fields['dst'].widget.attrs.update({'class': 'form_dst'})
        self.fields['title'].widget.attrs.update({'class': 'form_title'});

class LinkForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('title', 'link', 'tags')
        labels = {
            "title": "Title",
            "link": "Add Link",
            "tags": "Tags",
        }
    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form_title'});
        self.fields['link'].widget.attrs.update({'class': 'form_link'});

class YoutubeForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('youtube', 'dst', 'tags')
        labels = {
            "youtube": "YouTube Video Share Link",
            "dst": "Description",
            "tags": "Tags",
        }
    def __init__(self, *args, **kwargs):
        super(YoutubeForm, self).__init__(*args, **kwargs)
        self.fields['dst'].widget.attrs.update({'class': 'form_dst'})
        self.fields['youtube'].widget.attrs.update({'class': 'form_youtube'})

class InstaForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('insta',)
        labels = {
            "insta": "Instagram Post Share Link",
        }
    def __init__(self, *args, **kwargs):
        super(InstaForm, self).__init__(*args, **kwargs)
        self.fields['insta'].widget.attrs.update({'class': 'form_insta'})
