from django.contrib import admin

from ..models.genre import Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name', 'description', 'id')
