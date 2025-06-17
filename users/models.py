from django.contrib.auth.models import AbstractUser
from django.db import models

# Make sure your 'courses' app has a 'Subject' model defined.
# If not, you'll need to create that model first or adjust 'interests'
# to be a CharField with predefined choices if you don't want to link to Subjects.
from courses.models import Subject 

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="student")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # --- New Fields for Pedagogic Level and Interests ---
    PEDAGOGIC_LEVEL_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('university', 'University'),
        ('personal', 'Personal'),
    ]
    pedagogic_level = models.CharField(
        max_length=20,
        choices=PEDAGOGIC_LEVEL_CHOICES,
        blank=True,  # Allow it to be optional in the database
        null=True,   # Allow NULL in the database
        verbose_name="Pedagogic Level"
    )

    # Linking interests directly to your 'Subject' model from the 'courses' app.
    # This means users select from your defined course subjects as their interests.
    interests = models.ManyToManyField(
        Subject,
        related_name='interested_users',
        blank=True, # Allow users to have no interests selected initially
        verbose_name="Interests"
    )
    # ----------------------------------------------------

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"