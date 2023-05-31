from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render
from dash.models import JobPost
from dash.models import Submission
from django.http import FileResponse, Http404, HttpResponseNotFound



#def index(request):
#   return render(request,'index2.html')


#def indexpage(request):
#    jobs = JobPost.objects.order_by('-created_at')[:6]  # slice the queryset to get only the first 6 jobs
#    context = {'jobs': jobs}
#    return render(request, 'index.html', context)

def indexpage(request):
    jobs = JobPost.objects.order_by('-created_at')[:6]  # slice the queryset to get only the first 6 jobs
    context = {'jobs': jobs}
    return render(request, 'index.html', context)

def job_list(request):
    jobs = JobPost.objects.all()
    context = {'jobs': jobs}
    return render(request, 'jobs.html', context)




####
@login_required
def download_resume(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.user != request.user:
        # Only the owner of the submission can download the file
        return HttpResponseNotFound()

    file_path = submission.resume.path
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(submission.resume.name)
    return response

@login_required
def download_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.user != request.user:
        # Only the owner of the submission can download the file
        return HttpResponseNotFound()

    file_path = submission.resume.path
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(submission.resume.name)
    return response