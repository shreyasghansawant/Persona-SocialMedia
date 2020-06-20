from django.contrib import admin
from .models import Profile, Post, Follow, Notification, LikePost, CommentPost, Search

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Notification)
admin.site.register(LikePost)
admin.site.register(CommentPost)
admin.site.register(Search)
