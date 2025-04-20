

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Custom fields for your user model (if any)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='face_user_set',  # Change related_name to avoid clash
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='face_user_permissions_set',  # Change related_name to avoid clash
        blank=True
    )

def user_photo_path(instance, filename):
    return f'user_photos/{instance.user.username}/{filename}'

from django.conf import settings

class UserPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')


    def __str__(self):
        return f"{self.user.username}'s Photo"
class Subject(models.Model):
    topic=models.CharField(max_length=128)
    date=models.DateTimeField()

    def __str__(self):
        return f"attendance on {self.date} for subject {self.topic}"
class Student(models.Model):
    username=models.ForeignKey(User,on_delete=models.CASCADE)
    detail=models.ForeignKey(Subject,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f'student roll number {self.username.username} '


##for user photo use photo = some_user.userphoto.photo.url
    