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