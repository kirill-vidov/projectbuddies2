from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Categories, Post, Skills, Message, Profile, Portfolio, Notifications
from django.contrib.auth.models import User
from django.contrib.auth.forms import  UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm, CreateUserForm, ProfileForm
from django.contrib.auth.decorators import login_required
import json


def signUp(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Profile.objects.create(user=request.user)
            print(1)

            Notifications.objects.create(owner=request.user, message='Edit your profile to help people know you better', reminder=True)
            return redirect('home')

    return render(request, 'base/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')

    return render(request, 'base/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def frontPage(request):
    categories = Categories.objects.all()
    skills = Skills.objects.all()
    posts = Post.objects.order_by('-created')

    try:
        notifications = Notifications.objects.filter(owner=request.user)
    except:
        notifications = []

    if 'post' in request.POST:
        if request.user.is_authenticated:
            post = request.POST.get('post')
            post = Post.objects.get(id=post)
            user = User.objects.get(pk=post.host.id)
            notifications = Notifications.objects.filter(sender=request.user)

            post.requested.add(request.user)

            for noti in notifications:
                if post.id == noti.postToJoin.id:
                    return redirect('home')

            Notifications.objects.create(owner=user, sender=request.user, postToJoin=post, message=str(request.user).capitalize() + " Wants To Join - " + str(post))
        else:
            return redirect('login')

    if request.method == 'POST':
        if 'bookmark' in request.POST:
            if request.user.is_authenticated:
                post = request.POST.get('bookmark')
                post = Post.objects.get(id=post)
                post.bookmarks.add(request.user)
            else:
                return redirect('login')

        elif 'closeNotification' in request.POST:
            notification = request.POST['closeNotification']
            notification = Notifications.objects.get(id=notification)

            if notification.reminder == True:
                notification.delete()
            else:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.requested.remove(notification.sender)
                notification.delete()

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

        return redirect('home')

    context = {'categories': categories, 'posts': posts, 'skills': skills, 'notifications': notifications}
    return render(request, 'base/frontPage.html', context)


@login_required
def createProject(request):
    categories = Categories.objects.all()
    skills = Skills.objects.all()
    form = PostForm()
    notifications = Notifications.objects.filter(owner=request.user)

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
        else:
            form = PostForm(request.POST)
            skillsSelected = request.POST.getlist('skillsNeeded')
            categorySelected = request.POST.get('category')

            if form.is_valid():
                post = form.save(commit=False)
                post.host = request.user
                post.save()
                post.members.add(request.user)
                post.category.add(Categories.objects.get(id=categorySelected))

                try:
                    post.picture = request.FILES['image']
                except:
                    pass

                for num in skillsSelected:
                    post.skillsNeeded.add(Skills.objects.get(id=num))
                post.save()
                return redirect('home')

    context = {'categories': categories, 'form': form, 'skills': skills, 'notifications': notifications}
    return render(request, 'base/createProject.html', context)


@login_required
def userProjects(request):
    posts = Post.objects.filter(host=request.user)
    joinedPosts = request.user.members.all()
    notifications = Notifications.objects.filter(owner=request.user)

    if request.method == 'POST':
        if 'postID' in request.POST:
            post = Post.objects.get(id=request.POST['postID'])
            post.members.remove(request.user)

        elif 'closeProject' in request.POST:
            post = Post.objects.get(id=int(request.POST['closeProject']))
            post.delete()

        elif 'change-image' in request.POST:
            post = Post.objects.get(id=int(request.POST['change-image']))
            post.picture = request.FILES['image']
            post.save()

        elif 'closeNotification' in request.POST:
            notification = request.POST['closeNotification']
            notification = Notifications.objects.get(id=notification)

            if notification.reminder == True:
                notification.delete()
            else:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.requested.remove(notification.sender)
                notification.delete()

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

        return redirect('user-projects')

    context = {'posts': posts, 'joinedPosts': joinedPosts, 'notifications': notifications}
    return render(request, 'base/myProjects.html', context)


@login_required
def projectPage(request, pk):
    post = Post.objects.get(id=pk)
    messages = Message.objects.filter(post=post)[0:25]
    notifications = Notifications.objects.filter(owner=request.user)

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

            return redirect('project-page', pk)

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
        elif 'message' in request.POST:
            Message.objects.create(user=request.user, post=post, content=request.POST['message'])

            return redirect('project-page', pk)

    context = {'post': post, 'messages': messages, 'notifications': notifications}
    return render(request, 'base/projectPage.html', context)


@login_required
def bookmarks(request):
    posts = Post.objects.filter(bookmarks=request.user)
    notifications = Notifications.objects.filter(owner=request.user)

    if request.method == 'POST':
        if 'post' in request.POST:
            post = request.POST.get('post')
            post = Post.objects.get(id=post)
            user = User.objects.get(pk=post.host.id)
            notifications = Notifications.objects.filter(sender=request.user)

            for noti in notifications:
                if post.id == noti.postToJoin.id:
                    return redirect('home')

            Notifications.objects.create(owner=user, sender=request.user, postToJoin=post, message=str(request.user).capitalize() + " Wants To Join - " + str(post))

        elif 'remove' in request.POST:
            post = request.POST.get('remove')
            post = Post.objects.get(id=post)

            post.bookmarks.remove(request.user)

        elif 'closeNotification' in request.POST:
            notification = request.POST['closeNotification']
            notification = Notifications.objects.get(id=notification)

            if notification.reminder == True:
                notification.delete()
            else:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.requested.remove(notification.sender)
                notification.delete()

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

        return redirect('bookmarks')


    context = {'posts': posts, 'notifications': notifications}
    return render(request, 'base/bookmarks.html', context)


@login_required
def profile(request, pk):
    profile = Profile.objects.get(user=pk)
    projects = Portfolio.objects.filter(profile=profile)
    myPosts = Post.objects.filter(host=request.user)
    notifications = Notifications.objects.filter(owner=request.user)

    if request.method == 'POST':
        if 'delete-project' in request.POST:
            project = request.POST.get('delete-project')
            project = Portfolio.objects.get(id=project)
            project.delete()
        elif 'invitedPost' in request.POST:
            invitedPost = request.POST['invitedPost']
            invitedPost = Post.objects.get(id=invitedPost)

            Notifications.objects.create(owner=User.objects.get(id=pk), sender=request.user, postToJoin=invitedPost, invite=True, message= " Invited You To - " + str(invitedPost))


        elif 'closeNotification' in request.POST:
            notification = request.POST['closeNotification']
            notification = Notifications.objects.get(id=notification)

            if notification.reminder == True:
                notification.delete()
            else:
                post = Post.objects.get(id=notification.postToJoin.id)
                post.requested.remove(notification.sender)
                notification.delete()

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

        return HttpResponseRedirect(request.path_info)

    context = {'profile': profile, 'projects': projects, 'myPosts': myPosts, 'notifications': notifications}
    return render(request, 'base/profile.html', context)


@login_required
def editProfile(request):
    skills = Skills.objects.all()
    form = ProfileForm(instance = Profile.objects.get(user=request.user))
    profile = Profile.objects.get(user=request.user)
    notifications = Notifications.objects.filter(owner=request.user)

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
        else:
            if len(request.FILES) != 0:
                profile.profile_picture = request.FILES.get('profile_picture')

            form = ProfileForm(request.POST, request.FILES, request.FILES, instance = Profile.objects.get(user=request.user))
            if form.is_valid():
                form.save()

        return redirect('profile', pk=request.user.id)

    context = {'skills': skills, 'form': form, 'profile':profile, 'notifications': notifications}
    return render(request, 'base/editProfile.html', context)


@login_required
def createShowcase(request):
    user = Profile.objects.get(user=request.user)
    notifications = Notifications.objects.filter(owner=request.user)

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
        else:
            Portfolio.objects.create(profile=user, link=request.POST.get('link'), projectName=request.POST.get('name'), image=request.FILES.get('image'))

        return redirect('profile', pk=request.user.id)

    context = {'notifications': notifications}
    return render(request, 'base/postProject.html', context)
