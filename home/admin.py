from django.contrib import admin
from .models import Profile
# from .models import liveResult
# from .models import imageResult
from .models import ImageRes
from .models import LiveRes
# from .models import Testing
# from .models import Report

# Register your models here.
admin.site.register(Profile)
# admin.site.register(liveResult)
# admin.site.register(imageResult)
admin.site.register(ImageRes)
admin.site.register(LiveRes)

# admin.site.register(Testing)
# admin.site.register(Report)
