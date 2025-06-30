from django.contrib.auth.models import AbstractUser
from django.db import models
from courses.models import Subject

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    )

    PEDAGOGIC_LEVEL_CHOICES = (
        ('primaire', 'Prinmaire'),
        ('secondaire', 'Secondaire'),
        ('universitaire', 'Universitaire'),
        ('personnel', 'Personnel'),
    )

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    pedagogic_level = models.CharField(max_length=20, choices=PEDAGOGIC_LEVEL_CHOICES)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    interests = models.ManyToManyField(Subject, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username