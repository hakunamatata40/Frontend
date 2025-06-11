# courses/models.py
from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager
from django.template.loader import render_to_string
from django.utils.text import slugify

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='courses_created',
                                   limit_choices_to={'user_type': 'instructor'})
    subject = models.ForeignKey(Subject,
                                 on_delete=models.CASCADE,
                                 related_name='courses')
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # 0 for free courses
    is_published = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    # ADD THIS LINE FOR THE COURSE THUMBNAIL IMAGE
    image = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    # 'course_thumbnails/' will be a subfolder inside your MEDIA_ROOT (e.g., ehblo_project/media/course_thumbnails/)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('course_detail', args=[str(self.id), self.slug])


class Module(models.Model):
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='modules')
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ('order',)
        unique_together = ('course', 'title')

    def __str__(self):
        return f'{self.order}. {self.title}'


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Content(models.Model):
    module = models.ForeignKey(Module,
                               on_delete=models.CASCADE,
                               related_name='contents')
    title = models.CharField(max_length=250, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':(
                                         'textcontent',
                                         'videocontent',
                                         'imagecontent',
                                         'filecontent')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('order',)
        unique_together = ('module', 'order')

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.item.__class__.__name__}"

    def render(self):
        return render_to_string(f'courses/content/{self.item.__class__.__name__.lower()}.html', {'item': self.item})


class TextContent(models.Model):
    content = models.TextField()

    class Meta:
        verbose_name_plural = "Text Contents"
    def __str__(self):
        return "Text Content"

class VideoContent(models.Model):
    video_url = models.URLField(help_text="Paste YouTube, Vimeo, or direct video URL.")

    class Meta:
        verbose_name_plural = "Video Contents"
    def __str__(self):
        return "Video Content"

class ImageContent(models.Model):
    image = models.ImageField(upload_to='course_images/') # This is for images *within* modules

    class Meta:
        verbose_name_plural = "Image Contents"
    def __str__(self):
        return "Image Content"

class FileContent(models.Model):
    file = models.FileField(upload_to='course_files/')

    class Meta:
        verbose_name_plural = "File Contents"
    def __str__(self):
        return "File Content"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='enrollments',
                                 limit_choices_to={'user_type': 'student'})
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_contents = models.ManyToManyField(Content, blank=True, related_name='completed_by_students')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student.username} enrolled in {self.course.title}'

    def get_progress(self):
        total_contents = self.course.modules.aggregate(total=models.Count('contents'))['total']
        if not total_contents:
            return 0
        completed_count = self.completed_contents.count()
        return (completed_count / total_contents) * 100