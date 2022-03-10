from django.contrib import admin
from .models import Profile
from .models import liveResult
from .models import imageResult

# Register your models here.
admin.site.register(Profile)
admin.site.register(liveResult)
admin.site.register(imageResult)
