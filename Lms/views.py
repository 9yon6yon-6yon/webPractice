from django.utils.crypto import get_random_string
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import re
from django.urls import reverse
from django.conf import settings
from .models import *
from django.http import HttpResponse
import csv
from io import TextIOWrapper


def createForm(request):
    return render(request, 'create-user.html')


def createUser(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            # Process uploaded CSV file
            csv_text = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.reader(csv_text)
            for row in csv_reader:
                # Extract data from CSV row and create users
                # csv_username = row[0]
                csv_email = row[1]
                csv_user_type = row[2]
                csv_phone = row[3]

                csv_user = Users.objects.create_user(
                     email=csv_email, password="password", user_type=csv_user_type)
                csv_user.created_at = timezone.now()
                csv_user.updated_at = timezone.now()
                csv_user.save()

                # Create profile
                csv_profile = Profile.objects.create(
                    user=csv_user, phone=csv_phone)
                csv_profile.save()

            messages.success(
                request, 'Account(s) created successfully from CSV where default password is : password')
            return redirect('create')
        # If CSV file is not provided, process form data
        # username = request.POST['userName']
        email = request.POST['email']
        password = request.POST['password']
        user_type = request.POST['type']
        phone = request.POST['phone']
        user = Users.objects.create_user(
            email=email, password=password, user_type=user_type)
        user.created_at = timezone.now()
        user.updated_at = timezone.now()
        user.save()

        profile_picture = request.FILES.get('image_path')
        profile = Profile.objects.create(
            user=user, phone=phone, profile_picture=profile_picture)
        profile.save()
    messages.success(
        request, 'Account created successfully.')
    return redirect('create')


def index(request):
    return render(request, 'login.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.error(
                request, 'User not found or incorrect email/password.')
            return redirect('index')

        if check_password(password, user.password):
            auth_login(request, user)
            user.is_active = True
            user.save()
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            try:
                user_profile = Profile.objects.get(user=user)
                if user_profile.profile_picture:
                    request.session['user_profile_picture'] = user_profile.profile_picture.url
                else:
                    request.session['user_profile_picture'] = '/media/profile_pics/default-profile.png'
            except Profile.DoesNotExist:
                request.session['user_profile_picture'] = '/media/profile_pics/default-profile.png'
            return redirect('user.dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('index')

    else:
        return redirect('index')


def send_reset_link(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Users.objects.filter(email=email).exists():
            token = get_random_string(64)
            PasswordResetToken.objects.create(
                email=email, token=token, created_at=timezone.now())
            reset_url = request.build_absolute_uri(
                reverse('reset.password', kwargs={'token': token, 'email': email}))
            subject = 'Password Reset'
            context = {'reset_url': reset_url}
            html_message = render_to_string(
                'reset-password-email.html', context)
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
            )
            messages.success(
                request, 'A password reset link has been sent to your email accont.')
            return redirect('forget.password.form')
        else:
            messages.error(request, 'Invalid Email. Please try again.')
            return redirect('forget.password.form')
    else:
        messages.error(request, 'Bad request')
        return redirect('forget.password.form')


def forgotPassword(request):
    return render(request, 'forgot-password.html')


def reset_Password(request, token, email):
    context = {
        'token': token,
        'email': email,
    }
    return render(request, 'change-password.html', context)


def verify_password_strength(password):
    if len(password) < 6:
        return {'length': 'Password should be 6 characters or more.'}
    if not any(char.isdigit() for char in password):
        return {'digit': 'Password should contain at least one digit.'}
    if not re.search(r'[!@#$%^&*()_+\-=[\]{};\':"|,.<>/?]', password):
        return {'symbol': 'Password should contain at least one symbol.'}
    if not any(char.isupper() for char in password):
        return {'uppercase': 'Password should contain at least one uppercase letter.'}
    if not any(char.islower() for char in password):
        return {'lowercase': 'Password should contain at least one lowercase letter.'}
    return None


def save_Password(request):
    if request.method == 'POST':
        token = request.POST['token']
        email = request.POST['email']
        password = request.POST['password']
        password_confirmation = request.POST['password_confirmation']

        password_strength = verify_password_strength(password)

        if password_strength:
            for key, value in password_strength.items():
                messages.error(request, value)
                context = {
                    'token': token,
                    'email': email,
                }
            return render(request, 'change-password.html', context)

        if password != password_confirmation:
            messages.error(request, "Password and confirmation do not match.")
            return redirect('reset.password', token=token, email=email)

        try:
            check_token = PasswordResetToken.objects.get(
                email=email, token=token)
        except PasswordResetToken.DoesNotExist:
            messages.error(request, "Invalid token.")
            return redirect('reset.password', token=token, email=email)

        # Update user's password
        user = Users.objects.get(email=email)
        user.password = make_password(password)
        user.save()

        # Delete used token
        check_token.delete()

        messages.success(
            request, "Password reset successful. You can now log in with your new password.")
        return redirect('index')
    else:
        context = {
            'token': token,
            'email': email,
        }
        return render(request, 'change-password.html', context)

def home(request):
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id)
    unread_notification_count = Notification.objects.filter(
        user_id=user_id).count()
    unread_message_count = ChatMessage.objects.filter(
        receiver_id=user_id).count()

    try:
        user_profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        user_profile = None

    faculty = None
    courses_teaching = None
    student_courses = None
    student = None
    enrolled_courses = None

    if user.user_type == 'faculty':
        faculty = user
        courses_teaching = faculty.courses_assigned.all()
        student_courses = faculty.assigned_students.all()
    elif user.user_type == 'student':
        student = user
        enrolled_courses = student.enrolled_courses.all()

    context = {
        'unread_notification_count': unread_notification_count,
        'unread_message_count': unread_message_count,
        'user_profile': user_profile,
        'user': user,
        'faculty': faculty,
        'student': student,
        'courses_teaching': courses_teaching,
        'student_courses': student_courses,
        'enrolled_courses': enrolled_courses,
    }

    return render(request, 'dashboard.html', context)


def changePassword(request):
    return


def user_profile_view(request, user_id):
    user = get_object_or_404(Users, id=user_id)


    try:
        user_profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        user_profile = None

    context = {
        'user': user,
        'user_profile': user_profile,
    }

    return render(request, 'profile.html', context)


def logout(request):
    email = request.session.get('email')
    user = Users.objects.get(email=email)
    user.is_active = False
    user.save()
    auth_logout(request)
    return redirect('index')


def loadSettings(request):
    return render(request, 'settings.html')


def offline(request, id):
    user = get_object_or_404(Users, id=id)
    user.is_active = not user.is_active
    user.save()

    status_message = "offline" if user.is_active else "online"
    messages.success(request, f"Status changed to {status_message}")
    return redirect('user.settings')


def privateView(request):
    user_id = request.session.get('user_id')
    user_files = PrivateFiles.objects.filter(user=user_id)
    return render(request, 'private-file.html', {'user_files': user_files})


def privateFileSave(request):
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id)
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')
        for file in files:
            PrivateFiles.objects.create(user=user, file=file)
        messages.success(request, "Files saved successfully")
        return redirect('user.private.view')
    messages.error(request, "Problem occured while handeling the request")
    return render(request, 'private-file.html')


def privateFileDelete(request, id):
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id)
    private_file = get_object_or_404(PrivateFiles, id=id, user=user)

    private_file.file.delete()

    private_file.delete()

    messages.success(request, "File deleted successfully")
    return redirect('user.private.view')


def loadChat(request):
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id)

    active_users_same_courses = Users.objects.filter(    
    ).exclude(id=user_id)

    return render(request, 'chat.html', {'active_users_same_courses': active_users_same_courses})


def loadSpecificChat(request, id):
    logged_in_user_id = request.session.get('user_id')
    logged_in_user = Users.objects.get(id=logged_in_user_id)

    selected_user = get_object_or_404(Users, id=id)

    sent_messages = ChatMessage.objects.filter(
        sender_id=logged_in_user, receiver_id=selected_user)
    received_messages = ChatMessage.objects.filter(
        sender_id=selected_user, receiver_id=logged_in_user)

    all_messages = list(sent_messages) + list(received_messages)
    all_messages.sort(key=lambda x: x.timestamp, reverse=False)

    context = {'selected_user': selected_user, 'all_messages': all_messages}
    chat_content = render_to_string('chat-context.html', context)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return HttpResponse(chat_content)
    else:
        return render(request, 'chat.html', context)
    
def sendChat(request, id):
    if request.method == 'POST':
        logged_in_user_id = request.session.get('user_id')
        logged_in_user = Users.objects.get(id=logged_in_user_id)
        selected_user = get_object_or_404(Users, id=id)

        message_text = request.POST.get('message')
        print(message_text)
        print(selected_user)
        if message_text:
            ChatMessage.objects.create(
                sender=logged_in_user, receiver=selected_user, message=message_text)

    return redirect('user.chat.show', id=id)


def makeAnnouncement(request):
    return render(request, '')


def viewAnnouncement(request, id):
    return render(request, '')


def assignmentCreate(request):
    return render(request, '')


def assignmentView(request, id):
    return render(request, 'assignment-view.html')


def assignmentSubmit(request, id):
    return render(request, 'assignment-view.html')


def assignmentViewAll(request):
    return render(request, 'assignment-view.html')

def assign_courses_to_faculty(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty')
        course_ids = request.POST.getlist('courses')
        student_ids = request.POST.getlist('students')
        faculty = Users.objects.get(id=faculty_id)
        courses = Course.objects.filter(id__in=course_ids)
        students = Users.objects.filter(id__in=student_ids)
       

        for student in students:
            student.faculty = faculty
            student.save()

        unassigned_courses = courses.exclude(faculty=faculty)

        faculty.courses_assigned.set(unassigned_courses)
        student.enrolled_courses.set(unassigned_courses)

        messages.success(request, 'Course added successfully to the faculty')
        return redirect('assign.courses_to_faculty')

    faculties = Users.objects.filter(user_type='faculty')
    courses = Course.objects.all()
    students = Users.objects.filter(user_type='student')
    return render(request, 'assign_courses_to_faculty.html', {'faculties': faculties, 'courses': courses, 'students': students})

def courses(request):
    if request.method == 'POST':
        course_name = request.POST.get('name')
        course_category = request.POST.get('category')
        course_code = request.POST.get('code')

        course_credits = request.POST.get('credits')
        course_description = request.POST.get('description')

        Course.objects.create(name=course_name, category=course_category,
                              code=course_code, credits=course_credits, description=course_description)
        messages.success(request, 'Course added successfully')
        return redirect('add-course')

    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'courses.html', context)


def deletecourse(request, id):
    course = get_object_or_404(Course, id=id)
    course.delete()
    messages.success(request, 'Course deleted')
    return redirect('add-course')
