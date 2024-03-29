from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Categories, Post, Skills, Message, Profile, Portfolio, Notifications
from django.contrib.auth.models import User
from django.contrib.auth.forms import  UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm, CreateUserForm, ProfileForm
from django.contrib.auth.decorators import login_required
import json


def frontPage(request):
    categories = Categories.objects.all()
    skills = Skills.objects.all()
    posts = Post.objects.order_by('-created')

    try:
        notifications = Notifications.objects.filter(owner=request.user)
    except:
        notifications = []

    if 'post' in request.POST:
        post = request.POST.get('post')
        post = Post.objects.get(id=post)
        user = User.objects.get(pk=post.host.id)
        notifications = Notifications.objects.filter(sender=request.user)

        post.requested.add(request.user)

        for noti in notifications:
            if post.id == noti.postToJoin.id:
                return redirect('home')

        Notifications.objects.create(owner=user, sender=request.user, postToJoin=post, message=str(request.user).capitalize() + " Wants To Join - " + str(post))

    if request.method == 'POST':
        if 'bookmark' in request.POST:
            post = request.POST.get('bookmark')
            post = Post.objects.get(id=post)
            post.bookmarks.add(request.user)

        return redirect('home')

    context = {'categories': categories, 'posts': posts, 'skills': skills, 'notifications': notifications}
    return render(request, 'base/frontPage.html', context)


def notifications(request):
    if request.method == 'POST':
        if 'closeNotification' in request.POST:
            notification = request.POST['closeNotification']
            notification = Notifications.objects.get(id=notification)

            if notification.reminder == True:
                notification.delete()
            else:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.requested.remove(notification.sender)
                notification.delete()

            success = 'Notifications Deleted'
            return HttpResponse(success)

        elif 'accept' in request.POST:
            notification = request.POST['accept']
            notification = Notifications.objects.get(id=notification)

            if notification.invite == False:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.requested.remove(notification.sender)
                post.members.add(notification.sender)
                notification.delete()
            else:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.members.add(notification.owner)
                notification.delete()

            success = 'User Accepted'
            return HttpResponse(success)
