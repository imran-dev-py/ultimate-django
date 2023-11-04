from django.contrib import admin

from tags.models import Tag, TaggedItem


@admin.register(Tag)
class TaggedItemAdmin(admin.ModelAdmin):
    search_fields = ["label"]
