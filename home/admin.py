from django.contrib import admin
from .models import ImageRes
from .models import LiveRes
from .models import Prof

# Register your models here.

admin.site.register(ImageRes)
admin.site.register(LiveRes)
admin.site.register(Prof)

