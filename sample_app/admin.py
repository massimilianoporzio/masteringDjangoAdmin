from datetime import datetime

from django.contrib import admin
from django.utils.html import format_html

from sample_app.models import *


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    empty_value_display = 'Unknown'
    fieldsets = [
        ("Author Info", {'fields': ['name']}),
    ]
    list_display = ('name', 'createdDate', 'updatedDate',)
    list_per_page = 20

    search_fields = ('name',) #serve anche per fare autocomplete in edit dalle classi che hanno Authore come ForeignKey



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    empty_value_display = 'Unknown'
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
    list_display = ('question_text', 'refAuthor', 'has_been_published', 'pub_date', 'createdDate', 'updatedDate',
                    'colored_question_text','goToChoices',)
    list_display_links = ('question_text','refAuthor' )
    ordering = ('-pub_date',)
    date_hierarchy = 'pub_date' #mette il link per fare le tab a seconda di pub_date
    # list_editable = ('refAuthor',)
    list_per_page = 20

    #performance
    list_select_related = ('refAuthor',)

    list_filter = ('refAuthor',)
    # autocomplete_fields = ['refAuthor']
    # OPPURE
    raw_id_fields = ('refAuthor',)

    def has_been_published(self, obj):
        present = datetime.now()
        return obj.pub_date.date() < present.date()

    has_been_published.short_description = 'Published?' #titolo della colonna
    has_been_published.boolean = True  # METTE ICONA AL POSTO DI TRUE / FALSE

    def colored_question_text(self, obj):
        return format_html('<span style="color: #{};">{}</span>', "ff5733", obj.question_text, )

    def goToChoices(self, obj): # definisco una colonna con link alle choice che hanno question_id = al presente id (pk)
        return format_html(
            '<a class="button" href="/admin/sample_app/choice/?question__id__exact=%s" target="blank">Choices</a>&nbsp;' % obj.pk)

    goToChoices.short_description = 'Choices'
    goToChoices.allow_tags = True


# Register your models here.

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_text','votes','createdDate', 'updatedDate',)
    list_filter = ('question__refAuthor','question',)
    ordering = ('-createdDate',)
    list_per_page = 20
    search_fields = ('choice_text', 'question__refAuthor__name', 'question__question_text',)
    
    #performances
    list_select_related = ('question', 'question__refAuthor',)


admin.site.register(Choice,ChoiceAdmin)
