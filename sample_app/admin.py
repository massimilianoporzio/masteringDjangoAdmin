from django.contrib import admin
from sample_app.models import *


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Author Info", {'fields': ['name']}),
    ]
    list_display = ('name','createdDate','updatedDate',)
    list_per_page = 20

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Question information", {
            'fields': ('question_text',)
        }),
        ("Date", {
            'fields': ('pub_date',)
        }),
        ('The author', {
            'classes': ('collapse',),
            'fields': ('refAuthor',),
        }),
    ]
    list_display = ('question_text', 'refAuthor','pub_date','createdDate', 'updatedDate',)
    list_display_links = ( 'question_text','refAuthor')

# Register your models here.
admin.site.register(Choice)