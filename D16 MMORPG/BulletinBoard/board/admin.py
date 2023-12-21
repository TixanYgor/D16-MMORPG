from django.contrib import admin
from .models import Poster


class PosterAdmin(admin.ModelAdmin):
    list_display = ['title', 'text', 'author']
    list_filter = ['author']


admin.site.register(Poster, PosterAdmin)
