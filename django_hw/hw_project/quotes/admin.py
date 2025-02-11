from django.contrib import admin
from .models import Quote, Tag

# Register your models here.
admin.site.register(Quote)
admin.site.register(Tag)