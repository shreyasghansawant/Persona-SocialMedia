from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from PIL import Image
from io import BytesIO
from django.core.files import File
from taggit.managers import TaggableManager

def compress(image):
    im = Image.open(image)
    im_io = BytesIO()
    rgb_im = im.convert('RGB')
    rgb_im.save(im_io, 'JPEG', quality=70)
    new_image = File(im_io, name=image.name)
    return new_image

def img_size(value):
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 10MB.')

def vid_size(value):
    limit = 100 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 100MB.')

def aud_size(value):
    limit = 50 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 50MB.')

def dp_size(value):
    limit = 3 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 3MB.')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dp = models.ImageField(
    upload_to='ProfilePictures/',
    null=True,
    blank=True,
    validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg']), dp_size],
    help_text="Optional. File size limit: 3MB.",
    default="ProfilePictures/no_dp.png"
    )
    dob = models.DateField(default=timezone.now, help_text="Optional. Format: 'year-month-date'")
    bio = models.CharField(max_length=150, blank=True, help_text="Optional. 100 characters or fewer.")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        new_image = compress(self.dp)
        self.dp = new_image
        super().save(*args, **kwargs)

class Post(models.Model):

    vid = models.FileField(
    upload_to='videos/',
    null=True,
    validators = [FileExtensionValidator(allowed_extensions=['mp4', 'flv', 'mp3']), vid_size],
    help_text="Required. File size limit: 100MB."
    )
    img = models.ImageField(
    upload_to='images/',
    null=True,
    validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg']), img_size],
    help_text="Required. File size limit: 10MB."
    )
    aud = models.FileField(
    upload_to='audios/',
    null=True,
    validators=[FileExtensionValidator(allowed_extensions=['mp3', 'ogg', 'wav']), aud_size],
    help_text="Required. File size limit: 50MB."
    )

    txt = models.TextField(null=True)
    link = models.URLField(max_length=200, null=True, help_text="Required. 200 characters or fewer.")
    youtube = models.URLField(max_length=100, null=True, help_text="Required. 100 characters or fewer.")
    insta = models.URLField(max_length=100, null=True, help_text="Required. 100 characters or fewer.")

    title = models.CharField(max_length=100, null=True, help_text="Required. 100 characters or fewer.")
    dst = models.TextField(help_text="Optional. If description going out of post change the line.", blank=True)

    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    tags = TaggableManager(blank=True, help_text="A comma-separated list of tags. e.g. dope,cool,awesome,persona")

    def __str__(self):
        return self.author.username + ' - ' + str(self.id)

    def save(self, *args, **kwargs):
        if self.img:
            new_image = compress(self.img)
            self.img = new_image
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

class CommentPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

class Follow(models.Model):
    followed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_by")
    followed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_to")
    follow_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.followed_by.username + " - " + self.followed_to.username

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    a_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="a_user")
    date_time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    like = models.BooleanField(default=False)
    comment = models.BooleanField(default=False)
    follow = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)

class Search(models.Model):
    search_text = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
