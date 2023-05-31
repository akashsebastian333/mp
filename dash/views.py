from django import forms
from django.http import FileResponse, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import JobPostForm, SubmissionForm
from .models import JobPost, Submission
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Message
from .models import Submission
from .forms import MessageForm
from itertools import groupby
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.views.static import serve
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm

def profile_view(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)
    return render(request, 'profile_view.html', {'user_profile': user_profile})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm, ProfileAvatarForm

from django.views.generic.base import View
from django.http import HttpResponseNotFound, HttpResponse
from django.conf import settings
import os

class AvatarView(View):
    def get(self, request, pk, filename):
        avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars', str(pk), filename)
        if os.path.exists(avatar_path):
            with open(avatar_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='image/jpeg')
        else:
            return HttpResponseNotFound('File not found')
        
@login_required
def profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        avatar_form = ProfileAvatarForm(request.POST, request.FILES, instance=profile)

        if form.is_valid() and avatar_form.is_valid():
            form.save()
            avatar_form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
        avatar_form = ProfileAvatarForm(instance=profile)

    # check if any of the required fields in profile model is empty
    if not profile.full_name or not profile.address or not profile.skills or not profile.education or not profile.phoneno:
        # display script alert tag to complete the profile
        messages.warning(request, 'Please complete your profile to use this feature.')

    return render(request, 'profile.html', {'form': form, 'avatar_form': avatar_form, 'profile': profile})





@login_required
def pie_chart(request, job_title=None):
# Retrieve the data needed for the pie chart
    user = request.user
    job_posts = JobPost.objects.filter(user=user)
    if job_title:
        job_posts = job_posts.filter(title=job_title)

    submissions_data = Submission.objects.filter(job_post__in=job_posts)
# Group the submissions by company name and count the number of submissions
    companies = {}
    for submission in submissions_data:
        company_name = submission.job_post.title
        if company_name in companies:
            companies[company_name] += 1
        else:
            companies[company_name] = 1

# Convert the data into a format that can be used by the charting library
    chart_data = {
        'labels': list(companies.keys()),
        'data': list(companies.values())
    }

# Get all unique job titles for filtering
    unique_job_titles = job_posts.values_list('title', flat=True).distinct()

# Get the selected job title from the query parameter
    selected_job_title = request.GET.get('job_title', '')

# Filter the submissions if a job title is selected
    if selected_job_title:
        submissions_data = submissions_data.filter(job_post__title=selected_job_title)

# Render the template that will generate the pie chart and table of submissions
    return render(request, 'pie_chart.html', {'chart_data': chart_data, 'submissions_data': submissions_data, 'unique_job_titles': unique_job_titles, 'selected_job_title': selected_job_title})




@staff_member_required
def user_list(request):
    users = User.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_to_delete = User.objects.get(id=user_id)
        user_to_delete.delete()
        return redirect('user_list')
    context = {
        'users': users
    }
    return render(request, 'user_list.html', context)





@login_required
def reply_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id, recipient=request.user)
    initial_data = {
        'subject': f"Re: {message.subject}",
        'recipient': message.sender,
    }
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(sender=request.user)
            message.sender = request.user
            message.save()
            messages.success(request, 'Your reply has been sent.')
            print(message_id)
            print(request.user)

            return redirect('/dashboard/inbox')

    else:
        form = MessageForm(initial=initial_data)
    print(message_id)
    print(request.user)

    return render(request, 'communication/send_message.html', {'form': form})




@login_required
def inbox(request):
    messages = Message.objects.filter(Q(recipient=request.user) | Q(sender=request.user))
    usernames = set()
    unique_messages = []
    for message in messages:
        if message.sender.username not in usernames:
            usernames.add(message.sender.username)
            unique_messages.append({'sender__username': message.sender.username})
    unread_count = Message.objects.filter(recipient=request.user, unread=True).count()
    return render(request, 'communication/inbox.html', {'messages': unique_messages, 'unread_count': unread_count})



@login_required
def user_messages(request, username):
    received_messages = Message.objects.filter(sender__username=username, recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user, recipient__username=username)
    messages = (received_messages | sent_messages).order_by('-sent_at')
    for message in messages:
        if message.recipient == request.user and not message.read_at:
            message.read_at = timezone.now()
            message.save()
    unread_count = Message.objects.filter(recipient=request.user, read_at=None).count()
    return render(request, 'communication/user_messages.html', {'messages': messages, 'username': username, 'unread_count': unread_count})




@login_required
def submissions(request):
    user = request.user
    job_title = request.GET.get('job_title') # get the job title from the request parameter
    if job_title: # if job_title parameter is present
        job_posts = JobPost.objects.filter(user=user, title=job_title) # filter by user and job_title
    else:
        job_posts = JobPost.objects.filter(user=user)
    submissions = Submission.objects.filter(job_post__in=job_posts).order_by('-created_at')
    success_message = messages.get_messages(request)
    return render(request, 'submissions.html', {'submissions': submissions, 'success_message': success_message})





@login_required
def resume_view(request, submission_id):
    submission = Submission.objects.get(id=submission_id)
    user = request.user
    return render(request, 'resume_view.html', {'profile': profile,'submission': submission})

"""

@login_required
def submissions(request):
    user = request.user
    job_posts = JobPost.objects.filter(user=user)
    submissions = Submission.objects.filter(job_post__in=job_posts)
    success_message = messages.get_messages(request)
    return render(request, 'submissions.html', {'submissions': submissions, 'success_message': success_message})
"""

@login_required
def send_message(request, submission_id, message_id=None):
    submission = get_object_or_404(Submission, pk=submission_id, job_post__user=request.user)
    parent_message = get_object_or_404(Message, pk=message_id, recipient=request.user) if message_id else None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(sender=request.user)
            message.sender = request.user
            message.recipient = User.objects.get(username=submission.user.username)  # set the recipient to the submission user
            message.parent_message = parent_message
            message.save()
            messages.success(request, 'Your message has been sent.')
            return redirect('submissions')
    else:
        initial_data = {'parent_message': parent_message} if parent_message else {'recipient': submission.user.username}
        form = MessageForm(initial=initial_data)

    form.fields['recipient'].widget = forms.HiddenInput()
    return render(request, 'communication/send_message.html', {'form': form, 'submission': submission, 'parent_message': parent_message, 'recipient': submission.user.username})




@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('dashboard/profile')

    username = request.user.username
    job_posts = JobPost.objects.filter(user=request.user)
    message_count = Message.objects.filter(recipient=request.user, unread=False).count()
    if request.method == 'POST':
        if 'post_job' in request.POST:
            form = JobPostForm(request.POST)
            if form.is_valid():
                job_post = form.save(commit=False)
                job_post.user = request.user
                job_post.save()
                return redirect('dashboard')
        elif 'delete_job' in request.POST:
            job_id = request.POST.get('delete_job')
            job_post = JobPost.objects.get(id=job_id, user=request.user)
            job_post.delete()
            return redirect('dashboard')
    else:
        form = JobPostForm()
    return render(request, 'auth/mdashboard.html', {'username': username, 'form': form, 'job_posts': job_posts, 'message_count': message_count})





@login_required
def job_dashboard_view(request):
    username = request.user.username
    job_posts = JobPost.objects.filter(user=request.user).order_by('-created_at')
    submission_count = Submission.objects.filter(job_post__user=request.user).count()
    
    if request.method == 'POST':
        if 'post_job' in request.POST:
            form = JobPostForm(request.POST)
            if form.is_valid():
                job_post = form.save(commit=False)
                job_post.user = request.user
                job_post.save()
                return redirect('dashboard')
        elif 'delete_job' in request.POST:
            job_id = request.POST.get('delete_job')
            job_post = JobPost.objects.get(id=job_id, user=request.user)
            job_post.delete()
            return redirect('dashboard')
    else:
        form = JobPostForm()
    
    return render(request, 'auth/joblistings.html', {'username': username, 'form': form, 'job_posts': job_posts, 'submission_count': submission_count})










def index(request):
    if request.method == 'POST' and 'delete_job' in request.POST:
        job_id = request.POST.get('delete_job')
        try:
            job_post = JobPost.objects.get(id=job_id)
            job_post.delete()
            messages.success(request, 'Job post deleted successfully.')
        except JobPost.DoesNotExist:
            messages.error(request, 'Job post not found.')
    
    job_posts = JobPost.objects.order_by('-created_at')
    paginator = Paginator(job_posts, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'auth/index.html', {'page_obj': page_obj})




@login_required
def edit_job(request, job_id):
    job_post = get_object_or_404(JobPost, id=job_id)

    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES, instance=job_post)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.created_at = timezone.now()  # Set created_at time to current time
            job_post.save()
            return redirect('/dashboard/all')
        else:
            print(form.errors)
    else:
        form = JobPostForm(instance=job_post)

    return render(request, 'edit_job.html', {'form': form})



def search_jobs(request):
    query = request.GET.get('q')
    if query:
        # Search for job posts that contain the query string in their title, description or company name.
        job_posts = JobPost.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(company__icontains=query)
        ).order_by('-created_at')
    else:
        job_posts = JobPost.objects.all().order_by('-created_at')
    
    return render(request, 'search_jobs.html', {'job_posts': job_posts})

#def job_detail(request, job_id):
 #   job_post = get_object_or_404(JobPost, id=job_id)
 #   return render(request, 'job_details.html', {'job_post': job_post})

@login_required
def job_detail(request, job_id):
    job_post = get_object_or_404(JobPost, pk=job_id)
    
    # Check if the user has already applied for this job post
    previous_submission = Submission.objects.filter(user=request.user, job_post=job_post).first()
    if previous_submission:
        return render(request, 'alreadyapplied.html', {'job_post': job_post})
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.job_post = job_post
            submission.user = request.user
            submission.save()
            messages.success(request, 'Your resume has been submitted successfully.')
            return redirect('/dashboard/myapplications', pk=job_id)
    else:
        form = SubmissionForm()
    
    return render(request, 'sub.html', {'job_post': job_post, 'form': form})



"""
@login_required
def submissions(request):
    user = request.user
    submissions = Submission.objects.filter(job_post__user=user)
    return render(request, 'submissions.html', {'submissions': submissions})
"""

#@login_required
#def my_files(request):
#    submissions = Submission.objects.filter(user=request.user)
#    return render(request, 'my.html', {'submissions': submissions})

"""
@login_required
def my_files(request):
    submissions = Submission.objects.filter(user=request.user)
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        submission = get_object_or_404(Submission, pk=submission_id, user=request.user)
        submission.delete()
        messages.success(request, 'Your file has been deleted.')
        return redirect('my_files')
    
    return render(request, 'my.html', {'submissions': submissions})
"""
@login_required
def my_files(request):
    submissions = Submission.objects.filter(user=request.user)
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        submission = get_object_or_404(Submission, pk=submission_id, user=request.user)
        submission.delete()
        messages.success(request, 'Your file has been deleted.')
        return redirect('my_files')
    
    return render(request, 'my.html', {'submissions': submissions})


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

@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id, user=request.user)
    submission.delete()
    messages.success(request, 'Your file has been deleted.')
    return redirect('my_files')


"""" message """


#@login_required
#@user_passes_test(lambda user: user.is_authenticated)
#def protected_serve(request, path, document_root=None, show_indexes=False):
#    return serve(request, path, document_root, show_indexes)

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



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Submission
from .forms import SubmissionStatusUpdateForm

@login_required
def update_submission_status(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == 'POST':
        form = SubmissionStatusUpdateForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submission status updated successfully.')
            return redirect('submissions')
    else:
        form = SubmissionStatusUpdateForm(instance=submission)

    return render(request, 'update_submission_status.html', {'form': form})