from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class Skills(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='profile_pic.png')
    profession = models.CharField(max_length=20, default='programmer')
    bio = models.CharField(max_length=300, blank=True)
    country = CountryField()
    skills = models.ManyToManyField(Skills, related_name='skills', blank=True)

    def __str__(self):
        return str(self.user)


class Portfolio(models.Model):
    profile = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    projectName = models.CharField(max_length=50, blank=False, default='programmer')
    image = models.ImageField(null=True, blank=False, default='deafultImage.png')
    link = models.CharField(max_length=200, blank=False, default='None')


class Categories(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=100, default='red')
    icon = models.ImageField(null=True, default='deafultImage.png')

    def __str__(self):
        return str(self.name)


class Post(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    bookmarks = models.ManyToManyField(User, related_name='bookmarks', blank=True, default=None)
    description = models.CharField(max_length=380)
    members = models.ManyToManyField(User, related_name='members', blank=True)
    category = models.ManyToManyField(Categories, related_name='category', default=None)
    skillsNeeded = models.ManyToManyField(Skills, related_name='skillsNeeded', blank=True)
    picture = models.ImageField(default='none')
    created = models.DateTimeField(auto_now_add=True)
    requested =  models.ManyToManyField(User, related_name='requested', blank=True)

    def __str__(self):
        return str(self.name)


class Notifications(models.Model):
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=50, blank=True)
    sender = models.ForeignKey(User, related_name='sender' ,null=True, on_delete=models.CASCADE)
    postToJoin = models.ForeignKey(Post, null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    reminder = models.BooleanField(default=False)
    invite = models.BooleanField(default=False)


class Message(models.Model):
    post = models.ForeignKey(Post, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_sent',)


Post.objects.order_by("-created")
Notifications.objects.order_by("-timestamp")
