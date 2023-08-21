from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
class Users(AbstractBaseUser):
    username = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    password = models.CharField(max_length=255)
    USER_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    faculty = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_students')
    user_type = models.CharField(choices=USER_TYPES, max_length=10, default='student')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()


class Profile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone = models.CharField(max_length=25)

class PrivateFiles(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_files/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    edited_at = models.DateTimeField(default=timezone.now)



class Notification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    sender = models.ForeignKey(Users, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Users, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Course(models.Model):
    CATEGORY_CHOICES = (
        ('A', 'Language'),
        ('B', 'General Education'),
        ('C', 'Basic Sciences'),
        ('D', 'Mathematics'),
        ('E', 'Other Engineering'),
        ('F', 'Core Courses'),
        ('G', 'Elective Courses'),
        ('H', 'University required courses'),
        ('I', 'Final Year Design Project'),
    )

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    credits = models.DecimalField(max_digits=4, decimal_places=1, default=3.0)
    code = models.CharField(max_length=10)
    description = models.TextField()
    faculty = models.ManyToManyField(Users, related_name='courses_assigned', blank=True)
    students = models.ManyToManyField(Users, related_name='enrolled_courses', blank=True)
    resources = models.ManyToManyField('Resource', related_name='courses', blank=True)
    announcements = models.ManyToManyField('Announcement', related_name='courses', blank=True)

    def __str__(self):
        return self.name
class Marking(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()

class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file_upload = models.FileField(upload_to='resources/')
    resource_type = models.CharField(max_length=50, choices=[('lecture', 'Lecture'), ('video', 'Video'), ('other', 'Other')])
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    file_upload = models.FileField(upload_to='submissions/')
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

class Grade(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()

class Transcript(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()


class PasswordResetToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Password reset token for {self.email}"
  