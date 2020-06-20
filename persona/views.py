from django.shortcuts import render, redirect
from .models import Profile, Post, Follow, CommentPost, LikePost, Notification
from django.contrib.auth.models import User
from .forms import ProfileForm, SignUpForm, TextForm, AudioForm, VideoForm, ImageForm, UserEditForm, LinkForm, YoutubeForm, InstaForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
from django.core import serializers
import json

def tags(request):
    print("hahaha")

def go_to_detail(request, post_id):
    return redirect('persona:detail', post_id)

def go_to_profile(request, user_id):
    return redirect('persona:profile', user_id)

def go_to_my_profile(request):
    return redirect('persona:my-profile')

def about(request):
    return redirect('persona:index')

@login_required(login_url="persona:signup")
def notifications(request):
    if request.is_ajax():
        notifications = Notification.objects.filter(user=request.user, read=False)
        for n in notifications:
            n.read = True
            n.save()
        data = {'done': 'done'}
        return JsonResponse(data)
    else:
        return redirect('persona:index')

@login_required(login_url="persona:signup")
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Changed Successfully!', extra_tags='message-success')
            return redirect('persona:edit-profile')
        else:
            return render(request, 'change_password.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required(login_url="persona:signup")
def delete_account(request):
    if request.method == "POST":
        username = request.POST.get('c_username')
        if username == request.user.username:
            if request.user.is_authenticated:
                request.user.delete()
                messages.success(request, 'Account Deleted Permanently!', extra_tags='message-success')
                return redirect('persona:signup')
        else:
            messages.error(request, "Entered wrong username!", extra_tags='message-error')
            return redirect('persona:edit-profile')

@login_required(login_url="persona:signup")
def index(request):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    following = Follow.objects.filter(followed_by=request.user).order_by('?')
    users = User.objects.all().order_by('?')
    no_users = User.objects.all().count()
    no_users -= 1
    following_posts = Follow.objects.filter(followed_by=request.user)
    all_posts = Post.objects.all()
    for f in following_posts:
        all_posts = all_posts.exclude(author=f.followed_to)
    all_posts = all_posts.exclude(author=request.user)
    posts = Post.objects.all().order_by('-date', '-time')
    for p in all_posts:
        posts = posts.exclude(author=p.author)
    for f in following:
        users = users.exclude(username=f.followed_to.username)
    users = users.exclude(username=request.user.username)
    return_list = []
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        know_likes = know_likes.exclude(user=request.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(return_list, 5)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {
        'posts': page,
        'users': users,
        'no_users': no_users,
        'following': following,
        'no_notifications': no_notifications,
        'notifications': notifications,
    })

def detail(request, post_id):
    if request.user.is_authenticated:
        no_notifications = Notification.objects.filter(user=request.user, read=False).count()
        notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
        post = Post.objects.get(pk=post_id)
        no_likes = post.likepost_set.all().count()
        no_comments = post.commentpost_set.all().count()
        likes = post.likepost_set.all()
        know_likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        following = Follow.objects.filter(followed_by=request.user)
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        know_likes = know_likes.exclude(user=request.user)
        likes = likes.exclude(user=request.user)
        comments = post.commentpost_set.all()
        like = None
        try:
            likedit = post.likepost_set.get(user=request.user)
            if likedit:
                like = True
        except Exception:
            like = False
        following_author = None
        for f in following:
            if post.author == f.followed_to:
                following_author = True
            else:
                following_author = False
        tags = post.tags.all()
        return render(request, 'detail.html', {
            'post': post,
            'no_likes': no_likes,
            'no_comments': no_comments,
            'likes': likes,
            'know_likes': know_likes,
            'comments': comments,
            'like': like,
            'following': following_author,
            'no_notifications': no_notifications,
            'notifications': notifications,
            'tags': tags,
        })
    else:
        post = Post.objects.get(pk=post_id)
        no_likes = post.likepost_set.all().count()
        no_comments = post.commentpost_set.all().count()
        comments = post.commentpost_set.all()
        tags = post.tags.all()
        return render(request, 'visit_detail.html', {
            'post': post,
            'no_likes': no_likes,
            'no_comments': no_comments,
            'comments': comments,
            'tags': tags,
        })

@login_required(login_url="persona:signup")
def search(request):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    text = request.GET.get('search_txt')
    if text == "":
        return redirect('persona:index')
    following = Follow.objects.filter(followed_by=request.user)
    users = User.objects.filter(Q(username__icontains=text) | Q(first_name__icontains=text) | Q(last_name__icontains=text))
    no_users = User.objects.filter(Q(username__icontains=text) | Q(first_name__icontains=text) | Q(last_name__icontains=text)).count()
    for f in following:
        users = users.exclude(username=f.followed_to.username)
    users = users.exclude(username=request.user.username)
    posts = Post.objects.filter(Q(title__icontains=text) | Q(dst__icontains=text) | Q(txt__icontains=text) | Q(link__icontains=text))
    following_users = User.objects.filter(Q(username__icontains=text) | Q(first_name__icontains=text) | Q(last_name__icontains=text))
    for u in users:
        following_users = following_users.exclude(username=u.username)
    return_list = []
    tags = Tag.objects.filter(name__icontains=text)
    no_tags = Tag.objects.filter(name__icontains=text).count()
    tag_return_list = []
    for tag in tags:
        tag_posts = Post.objects.filter(tags__slug=tag).count()
        tag_return_list.append((tag, tag_posts))
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(return_list, 15)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    return render(request, 'search.html', {
        'posts': page,
        'users': users,
        'no_users': no_users,
        'following': following_users,
        'search_txt': text,
        'no_notifications': no_notifications,
        'notifications': notifications,
        'tags': tag_return_list,
        'no_tags': no_tags,
    })

@login_required(login_url="persona:signup")
def liked_posts(request):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    no_like = LikePost.objects.filter(user=request.user).count()
    posts_vid = Post.objects.all()
    liked_video =  LikePost.objects.filter(user=request.user)
    for like in liked_video:
        posts_vid = posts_vid.exclude(pk=like.post.id)
    posts_vid_2 = Post.objects.all()
    for post in posts_vid:
        posts_vid_2 = posts_vid_2.exclude(pk=post.id)
    for post in posts_vid_2:
        if post.img or post.aud or post.link or post.txt or post.insta:
            posts_vid_2 = posts_vid_2.exclude(pk=post.id)
    video_posts = posts_vid_2
    following = Follow.objects.filter(followed_by=request.user)
    vid_return_list = []    
    for vid_post in video_posts:
        vid_likes = vid_post.likepost_set.all()
        vid_likes = vid_likes.exclude(user=request.user)
        vid_know_likes = vid_post.likepost_set.all()
        for f in following:
            vid_likes = vid_likes.exclude(user=f.followed_to)
        for l in vid_likes:
            vid_know_likes = vid_know_likes.exclude(user=l.user)
        vid_know_likes = vid_know_likes.exclude(user=request.user)
        vid_return_list.append((vid_post, vid_post.likepost_set.filter(user=request.user), vid_post.likepost_set.all().count(), vid_post.commentpost_set.all().count(), vid_likes, vid_know_likes, vid_post.commentpost_set.all(), vid_post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(vid_return_list, 3)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    all_posts = Post.objects.all()
    liked_posts = LikePost.objects.filter(user=request.user)
    for like in liked_posts:
        all_posts = all_posts.exclude(pk=like.post.id)
    all_posts_2 = Post.objects.all()
    for post in all_posts:
        all_posts_2 = all_posts_2.exclude(pk=post.id)
    for post in all_posts_2:
        if post.img or post.vid or post.youtube or post.insta:
            all_posts_2 = all_posts_2.exclude(pk=post.id)
    posts = all_posts_2
    return_list = []
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    return render(request, 'explore.html', {
        'posts': return_list,
        'vid_posts': page,
        'no_notifications': no_notifications,
        'notifications': notifications,
        'like': "like",
        'no_like': no_like,
    })

@login_required(login_url="persona:signup")
def explore(request):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    posts_vid = Post.objects.all()
    for post in posts_vid:
        if post.img or post.aud or post.link or post.txt or post.insta:
            posts_vid = posts_vid.exclude(pk=post.id)
    video_posts = posts_vid
    following = Follow.objects.filter(followed_by=request.user)
    vid_return_list = []    
    for vid_post in video_posts:
        vid_likes = vid_post.likepost_set.all()
        vid_likes = vid_likes.exclude(user=request.user)
        vid_know_likes = vid_post.likepost_set.all()
        for f in following:
            vid_likes = vid_likes.exclude(user=f.followed_to)
        for l in vid_likes:
            vid_know_likes = vid_know_likes.exclude(user=l.user)
        vid_know_likes = vid_know_likes.exclude(user=request.user)
        vid_return_list.append((vid_post, vid_post.likepost_set.filter(user=request.user), vid_post.likepost_set.all().count(), vid_post.commentpost_set.all().count(), vid_likes, vid_know_likes, vid_post.commentpost_set.all(), vid_post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(vid_return_list, 3)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    all_posts = Post.objects.all()
    for post in all_posts:
        if post.vid or post.youtube or post.insta or post.img:
            all_posts = all_posts.exclude(pk=post.id)
    posts = all_posts
    return_list = []
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    return render(request, 'explore.html', {
        'posts': return_list,
        'vid_posts': page,
        'no_notifications': no_notifications,
        'notifications': notifications,
    })

@login_required(login_url="persona:signup")
def tags(request, tag_slug):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    tag = Tag.objects.get(slug=tag_slug)
    no_tags = Post.objects.filter(tags__name__in=[tag]).count()
    posts_vid = Post.objects.filter(tags__name__in=[tag])
    for post in posts_vid:
        if post.img or post.aud or post.link or post.txt or post.insta:
            posts_vid = posts_vid.exclude(pk=post.id)
    video_posts = posts_vid
    following = Follow.objects.filter(followed_by=request.user)
    vid_return_list = []    
    for vid_post in video_posts:
        vid_likes = vid_post.likepost_set.all()
        vid_likes = vid_likes.exclude(user=request.user)
        vid_know_likes = vid_post.likepost_set.all()
        for f in following:
            vid_likes = vid_likes.exclude(user=f.followed_to)
        for l in vid_likes:
            vid_know_likes = vid_know_likes.exclude(user=l.user)
        vid_know_likes = vid_know_likes.exclude(user=request.user)
        vid_return_list.append((vid_post, vid_post.likepost_set.filter(user=request.user), vid_post.likepost_set.all().count(), vid_post.commentpost_set.all().count(), vid_likes, vid_know_likes, vid_post.commentpost_set.all(), vid_post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(vid_return_list, 3)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    all_posts = Post.objects.filter(tags__name__in=[tag])
    for post in all_posts:
        if post.vid or post.youtube or post.insta or post.img:
            all_posts = all_posts.exclude(pk=post.id)
    posts = all_posts
    return_list = []
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    return render(request, 'explore.html', {
        'posts': return_list,
        'vid_posts': page,
        'no_notifications': no_notifications,
        'notifications': notifications,
        'tag': tag,
        'no_tags': no_tags,
    })

def get_image_ajax(request):
    posts = Post.objects.all()
    for post in posts:
        if post.vid or post.txt or post.link or post.insta or post.aud or post.youtube:
            posts = posts.exclude(pk=post.id)
    images = posts
    likes = []
    comments = []
    for image in images:
        likes.append(image.likepost_set.all().count())
        comments.append(image.commentpost_set.all().count())
    json_images = serializers.serialize('json', images)
    img = json.loads(json_images)
    data = {
        'images': img, 
        'likes': likes,
        'media_url': settings.MEDIA_URL, 
        'comments': comments, 
    }
    return JsonResponse(data, safe=False)

def get_image_ajax_liked(request):
    posts = Post.objects.all()
    liked = LikePost.objects.filter(user=request.user)
    for like in liked:
        posts = posts.exclude(pk=like.post.id)
    posts_2 = Post.objects.all()
    for post in posts:
        posts_2 = posts_2.exclude(pk=post.id)
    for post in posts_2:
        if post.vid or post.txt or post.link or post.insta or post.aud or post.youtube:
            posts_2 = posts_2.exclude(pk=post.id)
    images = posts_2
    likes = []
    comments = []
    for image in images:
        likes.append(image.likepost_set.all().count())
        comments.append(image.commentpost_set.all().count())
    json_images = serializers.serialize('json', images)
    img = json.loads(json_images)
    data = {
        'images': img, 
        'likes': likes,
        'media_url': settings.MEDIA_URL, 
        'comments': comments, 
    }
    return JsonResponse(data, safe=False)

def get_image_ajax_tags(request):
    tag = request.GET['tag']
    posts = Post.objects.filter(tags__name__in=[tag])
    for post in posts:
        if post.vid or post.txt or post.link or post.insta or post.aud or post.youtube:
            posts = posts.exclude(pk=post.id)
    images = posts
    likes = []
    comments = []
    for image in images:
        likes.append(image.likepost_set.all().count())
        comments.append(image.commentpost_set.all().count())
    json_images = serializers.serialize('json', images)
    img = json.loads(json_images)
    data = {
        'images': img, 
        'likes': likes,
        'media_url': settings.MEDIA_URL, 
        'comments': comments, 
    }
    return JsonResponse(data, safe=False)

def get_image_detail(request):
    post_id = request.GET['post_id']
    post = Post.objects.get(pk=post_id)
    json_post = serializers.serialize('json', [post,])
    img = json.loads(json_post)
    json_author = serializers.serialize('json', [post.author,])
    author = json.loads(json_author)
    json_profile = serializers.serialize('json', [post.author.profile,])
    profile = json.loads(json_profile)
    likes = post.likepost_set.all().count()
    comments = post.commentpost_set.all().count()
    liked = None
    try:
        liked_post = LikePost.objects.get(user=request.user, post=post)
        if liked_post:
            liked = True
    except Exception:
        liked = False
    dst = True
    json_comments = serializers.serialize('json', post.commentpost_set.all())
    all_comments = json.loads(json_comments)
    data = {
        'image': img,
        'author': author,
        'profile': profile,
        'media_url': settings.MEDIA_URL,
        'likes': likes,
        'comments': comments,
        'liked': liked,
        'dst': dst,
        'all_comments': all_comments,
    }
    return JsonResponse(data)

@login_required(login_url="persona:signup")
def add_image(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.title = "!@#$%^&*()"
            inst.save()
            form.save_m2m()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'image': 'image',
            })
    else:
        form = ImageForm()
        return render(request, 'post_form.html', {
            'form': form,
            'image': 'image',
        })

@login_required(login_url="persona:signup")
def add_video(request):
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.save()
            form.save_m2m()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'video': 'audio',
            })
    else:
        form = VideoForm()
        return render(request, 'post_form.html', {
            'form': form,
            'video': 'audio',
        })

@login_required(login_url="persona:signup")
def add_audio(request):
    if request.method == "POST":
        form = AudioForm(request.POST, request.FILES)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.save()
            form.save_m2m()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'audio': 'audio',
            })
    else:
        form = AudioForm()
        return render(request, 'post_form.html', {
            'form': form,
            'audio': 'audio',
        })

@login_required(login_url="persona:signup")
def add_text(request):
    if request.method == "POST":
        form = TextForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.title = "!@#$%^&*()"
            inst.save()
            form.save_m2m()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'text': 'text',
            })
    else:
        form = TextForm()
        return render(request, 'post_form.html', {
            'form': form,
            'text': 'text',
        })

@login_required(login_url="persona:signup")
def add_link(request):
    if request.method == "POST":
        form = LinkForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.save()
            form.save_m2m()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'link': 'link',
            })
    else:
        form = LinkForm()
        return render(request, 'post_form.html', {
            'form': form,
            'link': 'link',
        })

@login_required(login_url="persona:signup")
def add_youtube(request):
    if request.method == "POST":
        form = YoutubeForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.youtube = inst.youtube[17:28]
            inst.title = "!@#$%^&*()"
            inst.save()
            form.save_m2m()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'youtube': 'youtube',
            })
    else:
        form = YoutubeForm()
        return render(request, 'post_form.html', {
            'form': form,
            'youtube': 'youtube',
        })

@login_required(login_url="persona:signup")
def add_insta(request):
    if request.method == "POST":
        form = InstaForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user
            inst.title = "!@#$%^&*()"
            inst.save()
            return redirect('persona:index')
        else:
            return render(request, 'post_form.html', {
                'form': form,
                'instagram': 'instagram',
            })
    else:
        form = InstaForm()
        return render(request, 'post_form.html', {
            'form': form,
            'instagram': 'instagram',
        })

@login_required(login_url="persona:signup")
def edit_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post.author == request.user:
        if post.img:
            if request.method == "POST":
                form = ImageForm(request.POST, request.FILES, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'image': 'image',
                        'edit': 'edit',
                    })
            else:
                form = ImageForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'image': 'image',
                    'edit': 'edit',
                })
        elif post.vid:
            if request.method == "POST":
                form = VideoForm(request.POST, request.FILES, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'video': 'video',
                        'edit': 'edit',
                    })
            else:
                form = VideoForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'video': 'video',
                    'edit': 'edit',
                })
        elif post.aud:
            if request.method == "POST":
                form = AudioForm(request.POST, request.FILES, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'audio': 'audio',
                        'edit': 'edit',
                    })
            else:
                form = AudioForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'audio': 'audio',
                    'edit': 'edit',
                })
        elif post.txt:
            if request.method == "POST":
                form = TextForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'text': 'text',
                        'edit': 'edit',
                    })
            else:
                form = TextForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'text': 'text',
                    'edit': 'edit',
                })
        elif post.link:
            if request.method == "POST":
                form = LinkForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'link': 'link',
                        'edit': 'edit',
                    })
            else:
                form = LinkForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'link': 'link',
                    'edit': 'edit',
                })
        elif post.youtube:
            if request.method == "POST":
                form = YoutubeForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'youtube': 'youtube',
                        'edit': 'edit',
                    })
            else:
                form = YoutubeForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'youtube': 'youtube',
                    'edit': 'edit',
                })
        elif post.insta:
            if request.method == "POST":
                form = InstaForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Edited Successfully!", extra_tags='message-success')
                    return redirect('persona:detail', post.id)
                else:
                    return render(request, 'post_form.html', {
                        'form': form,
                        'insta': 'insta',
                        'edit': 'edit',
                    })
            else:
                form = InstaForm(instance=post)
                return render(request, 'post_form.html', {
                    'form': form,
                    'insta': 'insta',
                    'edit': 'edit',
                })

@login_required(login_url="persona:signup")
def delete_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(pk=post_id)
        if post.author == request.user:
            post.delete()
            messages.success(request, "Post Deleted Successfully!", extra_tags='message-success')
            return redirect('persona:my-profile')

def signup_form(request):
    if request.user.is_authenticated:
        return redirect('persona:index');
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            users = User.objects.all()
            for one_user in users:
                if one_user.email == instance.email:
                    message = 'This email is in use already'
                    return render(request, 'signup.html', {
                        'form': form,
                        'message': message,
                    })
            instance.username = instance.username.lower()
            user = form.save()
            subject = "Welcome to Persona"
            html_content = render_to_string('mail.html', {'the_user': request.user}) # render with dynamic value
            text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.
            frm = settings.EMAIL_HOST_USER
            send_mail(subject, text_content, frm, [user.email,], html_message=html_content, fail_silently=True)
            profile = Profile.objects.create(user=user)
            profile.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('persona:new-profile')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

def login_form(request):
    if request.user.is_authenticated:
        return redirect('persona:my-profile');
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            subject = "Someone just Logged in to your Account."
            html_content = render_to_string('mail_2.html', {'the_user': request.user}) # render with dynamic value
            text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.
            frm = settings.EMAIL_HOST_USER
            send_mail(subject, text_content, frm, [user.email,], html_message=html_content, fail_silently=True)
            return redirect('persona:index')
        else:
            error = 'Please enter a correct username and password. Note that both fields may be case-sensitive.'
            return render(request, 'login.html', {
                'form': form,
                'error': error,
            })
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

@login_required(login_url="persona:signup")
def logout_form(request):
    logout(request)
    return redirect('persona:index')

@login_required(login_url="persona:signup")
def new_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('persona:index')
        else:
            return render(request, 'edit_profile.html', {
                'form': form,
                'new_user': 'new_user',
            })
    else:
        form = ProfileForm(instance=profile)
        return render(request, 'edit_profile.html', {
            'form': form,
            'new_user': 'new_user',
        })

@login_required(login_url="persona:signup")
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
        user_form = UserEditForm(request.POST or None, instance=request.user)
        print(form.errors, user_form.errors)
        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()
            messages.success(request, 'Persona Edited Successfully!', extra_tags='message-success')
            return redirect('persona:my-profile')
        else:
            return render(request, 'edit_profile.html', {
                'form': form,
                'user_form': user_form,
            })
    else:
        form = ProfileForm(instance=profile)
        user_form = UserEditForm(instance=request.user)
        return render(request, 'edit_profile.html', {
            'form': form,
            'user_form': user_form,
        })

@login_required(login_url="persona:signup")
def my_profile(request):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-date', '-time')
    no_posts = Post.objects.filter(author=user).count()
    following = Follow.objects.filter(followed_by=user)
    followers = Follow.objects.filter(followed_to=user)
    only_followers = Follow.objects.filter(followed_to=user)
    no_followers = Follow.objects.filter(followed_to=user).count()
    for f in following:
        only_followers = only_followers.exclude(followed_by=f.followed_to)
    for f in only_followers:
        followers = followers.exclude(followed_by=f.followed_by)
    return_list = []
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        know_likes = know_likes.exclude(user=request.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(return_list, 5)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    return render(request, 'my_profile.html', {
        'user': user,
        'posts': page,
        'following': following,
        'followers': followers,
        'only_followers': only_followers,
        'no_followers': no_followers,
        'no_posts': no_posts,
        'no_notifications': no_notifications,
        'notifications': notifications,
    })

def profile(request, user_id):
    no_notifications = Notification.objects.filter(user=request.user, read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
    user = User.objects.get(pk=user_id)
    if user == request.user:
        return redirect('persona:my-profile')
    try:
        check_follow = Follow.objects.get(followed_by=request.user, followed_to=user)
        if check_follow:
            follow = True
    except Exception:
        follow = False
    try:
        check_follow_back = Follow.objects.get(followed_by=user, followed_to=request.user)
        if check_follow_back:
            follow_back = True
    except Exception:
        follow_back = False
    posts = Post.objects.filter(author=user).order_by('-date', '-time')
    no_posts = Post.objects.filter(author=user).count()
    no_following = Follow.objects.filter(followed_by=user).count()
    no_followers = Follow.objects.filter(followed_to=user).count()
    following = Follow.objects.filter(followed_by=user)
    f_following = Follow.objects.filter(followed_by=user)
    followers = Follow.objects.filter(followed_to=user)
    f_followers = Follow.objects.filter(followed_to=user)
    i_follow = Follow.objects.filter(followed_by=request.user)
    for i in i_follow:
        f_following = f_following.exclude(followed_to=i.followed_to)
        f_following = f_following.exclude(followed_to=request.user)
    for f in f_following:
        following = following.exclude(followed_to=f.followed_to)
    for i in i_follow:
        f_followers = f_followers.exclude(followed_by=i.followed_to)
    f_followers = f_followers.exclude(followed_by=request.user)
    for f in f_followers:
        followers = followers.exclude(followed_by=f.followed_by)
    followers = followers.exclude(followed_by=request.user)
    return_list = []
    for post in posts:
        likes = post.likepost_set.all()
        likes = likes.exclude(user=request.user)
        know_likes = post.likepost_set.all()
        for f in following:
            likes = likes.exclude(user=f.followed_to)
        for l in likes:
            know_likes = know_likes.exclude(user=l.user)
        know_likes = know_likes.exclude(user=request.user)
        return_list.append((post, post.likepost_set.filter(user=request.user), post.likepost_set.all().count(), post.commentpost_set.all().count(), likes, know_likes, post.commentpost_set.all(), post.tags.all()))
    page_no = request.GET.get('page', 1)
    paginator = Paginator(return_list, 5)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
         page = paginator.page(1)
    except EmptyPage:
         page = paginator.page(paginator.num_pages)
    return render(request, 'profile.html', {
        'user': user,
        'posts': page,
        'no_posts': no_posts,
        'following': following,
        'followers': followers,
        'f_followers': f_followers,
        'f_following': f_following,
        'no_followers': no_followers,
        'no_following': no_following,
        'follow': follow,
        'follow_back': follow_back,
        'no_notifications': no_notifications,
        'notifications': notifications,
    })

def like_post_it(request):
    if request.method == "GET":
        post_id = request.GET['post_id']
        post = Post.objects.get(pk=post_id)
        try:
            liked = LikePost.objects.get(user=request.user, post=post)
            if liked:
                liked.delete()
                try:
                    notification = Notification.objects.get(user=post.author, a_user=request.user, like=True)
                    notification.delete()
                except Exception:
                    print("Notification not found")
                data = {
                    'likes': LikePost.objects.filter(post=post).count(),
                    'unlikedit': 'unlike',
                }
                return JsonResponse(data)
        except Exception:
            like = LikePost.objects.create(user=request.user, post=post)
            like.save()
            if request.user == post.author:
                print("hdjhjdhfjhsj")
            else:
                notification = Notification.objects.create(user=post.author, a_user=request.user, like=True, post=post)
                notification.save()
            data = {
                'likes': LikePost.objects.filter(post=post).count(),
                'likedit': 'like',
            }
            return JsonResponse(data)

@login_required(login_url="persona:signup")
def comment_post(request, post_id):
    if request.method == "GET":
        c_txt = request.GET.get('comment_txt')
        if c_txt == "":
            return redirect('persona:index')
        post = Post.objects.get(pk=post_id)
        comment = CommentPost.objects.create(user=request.user, post=post, comment=c_txt)
        comment.save()
        return redirect('persona:detail', post.id)

@login_required(login_url="persona:signup")
def delete_comment(request, comment_id, post_id):
    if request.method == "POST":
        comment = CommentPost.objects.get(pk=comment_id)
        post = comment.post
        if comment.user == request.user:
            comment.delete()
        return redirect('persona:detail', comment.post.id)

@login_required(login_url="persona:signup")
def follow_it(request):
    if request.method == "GET":
        user_id = request.GET['user_id']
        user = User.objects.get(pk=user_id)
        try:
            followed = Follow.objects.get(followed_by=request.user, followed_to=user)
            if followed:
                followed.delete()
                try:
                    notification = Notification.objects.get(user=user, a_user=request.user, follow=True)
                    notification.delete()
                except Exception:
                    print("Notification not found")
                data = {
                    'unfollowed': 'unfollow',
                    'followers': Follow.objects.filter(followed_to=user).count(),
                    'my_following': Follow.objects.filter(followed_by=request.user).count(),
                }
                return JsonResponse(data)
        except Exception:
            follow = Follow.objects.create(followed_by=request.user, followed_to=user)
            follow.save()
            notification = Notification.objects.create(user=user, a_user=request.user, follow=True)
            notification.save()
            data = {
                'followed': 'follow',
                'followers': Follow.objects.filter(followed_to=user).count(),
                'my_following': Follow.objects.filter(followed_by=request.user).count(),
            }
            return JsonResponse(data)

def share_gmail(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            gmail = request.GET['to_gmail']
            post_id = request.GET['post_id']
            post = Post.objects.get(pk=post_id)
            subject = request.user.username + " shared you a post."
            frm = settings.EMAIL_HOST_USER
            html_content = render_to_string('gmail.html', {'user': request.user, 'post': post}) # render with dynamic value
            text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.
            frm = request.user.email
            send_mail(subject, text_content, frm, [gmail,], html_message=html_content, fail_silently=False)
            data = {"done": "done"}
            return JsonResponse(data)

def comment_it(request):
    if request.method == "GET":
        post_id = request.GET['post_id']
        post = Post.objects.get(pk=post_id)
        comment_txt = request.GET['comment_txt']
        if comment_txt == '':
            return JsonResponse()
        comment = CommentPost.objects.create(user=request.user, comment=comment_txt, post=post)
        comment.save()
        if post.author == request.user:
            print("This is user!")
        else:
            notification = Notification.objects.create(user=post.author, a_user=request.user, post=post, comment=True)
            notification.save()
        no_comments = CommentPost.objects.filter(post=post).count()
        data = {'c_id': comment.id, 'no_comments': no_comments}
        return JsonResponse(data)

def delete_comment_it(request):
    if request.method == "POST":
        comment_id = request.POST['c_id']
        comment = CommentPost.objects.get(pk=comment_id)
        post = Post.objects.get(pk=comment.post.id)
        try:
            notification = Notification.objects.get(a_user=request.user, post=post, comment=True)
            notification.delete()
        except Exception:
            print("No Notification Found!")
        comment.delete()
        no_comments = CommentPost.objects.filter(post=post).count()
        data = {
            'no_comments': no_comments,
            'post_id_for_index': comment.post.id,
        }
        return JsonResponse(data)