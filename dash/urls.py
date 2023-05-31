from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import serve
from django.conf.urls.static import static
from .views import AvatarView



urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('/joblistings', views.job_dashboard_view, name='dashboard'),
    path('/all', views.index, name='dashboard'),
    path('/edit_job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('/search', views.search_jobs, name='search_jobs'),
    path('/jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('/submissions/', views.submissions, name='submissions'),
    path('/myapplications/', views.my_files, name='my_files'),
    path('/submissions/<int:submission_id>/download/', views.download_submission, name='download_submission'),
    path('/send_message/<int:submission_id>/', views.send_message, name='send_message'),
    path('/inbox', views.inbox, name='inbox'),
    path('/reply_message/<int:message_id>/', views.reply_message, name='reply_message'),
    path('/user_messages/<str:username>/', views.user_messages, name='user_messages'),
    path('/allusers', views.user_list, name='user_list'),
    #path('resumes/<path:path>', views.protected_serve, {'document_root': settings.STATICFILES_DIRS}),
    #path('/resumes/<int:pk>/download/', views.login_required(views.download_resume), name='download_resume'),
     path('/pie', views.pie_chart, name='pie_chart'),
    path('/profile', views.profile, name='profile'),
     path('/profile/<str:username>/', views.profile_view, name='profile_view'),
    path('/avatars/<int:pk>/<str:filename>/', AvatarView.as_view(), name='avatar-view'),
        path('/update_submission_status/<int:submission_id>/', views.update_submission_status, name='update_submission_status'),
        path('/resume/<int:submission_id>/', views.resume_view, name='resume_view'),


    # other URL patterns go here
]
