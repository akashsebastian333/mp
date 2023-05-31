from django.urls import path

from . import views

urlpatterns = [
    path('', views.indexpage, name='indexpage'),
    #path('hello', views.job_list, name='job_list'),
    path('jobs', views.job_list, name='job_list'),
    path('/resumes/<int:pk>/download/', views.download_submission, name='download_resume'),
]