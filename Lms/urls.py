
from django.conf.urls.static import static
from django.urls import path
from .views import *


urlpatterns = [

    path('create/', createForm, name='create'),
    path('create-user/', createUser, name='create-user'),
    path('', index, name='index'),
    path('user/login/', login, name='user-login'),
    path('user/forgot-password/', forgotPassword, name='forget.password.form'),
    path('user/reset-password/', send_reset_link, name='forget.password.link'),
    path('user/reset-new-password/<str:token>/<str:email>',
         reset_Password, name='reset.password'),
    path('user/save-new-password/', save_Password, name='save.password'),
    path('user/change-password', changePassword, name='change.password'),
    path('user/dashboard', home, name='user.dashboard'),
    path('user/profile/<int:user_id>/',
         user_profile_view, name='user.profile'),
    path('user/logout/', logout, name='user.logout'),
    path('user/offline/<int:id>/', offline, name='user.offline'),
    path('user/settings/', loadSettings, name='user.settings'),
    path('user/private-files-view/', privateView, name='user.private.view'),
    path('user/private-files-save/', privateFileSave, name='user.private.save'),
    path('user/private-files-delete/<int:id>',
         privateFileDelete, name='user.private.delete'),
    path('user/chat/view/', loadChat, name='user.chat.view'),
    path('user/chat/show/<int:id>/', loadSpecificChat, name='user.chat.show'),
    path('user/chat/send/<int:id>/', sendChat, name='user.chat.send'),
    # Optional id parameter
    path('user/chat/send/', sendChat, name='user.chat.send.optional'),
    # announcements and assignments done by faculty
    path('user/announcement-make', makeAnnouncement, name='makeAnnouncement'),
    path('user/announcement-view/<int:id>',
         viewAnnouncement, name='viewAnnouncement'),
    path('user/assignment-create', assignmentCreate, name='assignmentCreate'),
    path('user/assignment-submit/<int:id>/',
         assignmentSubmit, name='assignmentSubmit'),
    path('user/assignment-view/<int:id>/',
         assignmentView, name='assignmentView'),
    path('user/assignment-view-submissions/',
         assignmentViewAll, name='assignmentViewAll'),
    # assign courses to faculty and students by admin
    path('assign-faculty-to-students/', assign_faculty_to_students,
         name='assign.faculty_to_students'),
    path('assign-courses-to-faculty/', assign_courses_to_faculty,
         name='assign.courses_to_faculty'),
    path('courses/add/', courses, name='add-course'),
    path('courses/delete/<int:id>', deletecourse, name='delete-course'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
