from django.contrib import admin

from ..models.person import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('full_name', 'id')
