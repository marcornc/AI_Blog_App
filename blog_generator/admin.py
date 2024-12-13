from django.contrib import admin
from .models import BlogPost

# Register your models here.

# to be able to see the db in the admin pannel
admin.site.register(BlogPost)