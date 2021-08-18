import csv
from datetime import datetime, timedelta

from django.contrib import admin
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html
from django.utils import timezone

from django.contrib.auth.models import Group, User

from sample_app.models import *

class QuestionInline(admin.StackedInline):
    model = Question

class QuestionPublishedListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('Published questions')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'pub_date'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('Published', ('Published questions')),
            ('Unpublished', ('Unpublished questions')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'Published':
            return queryset.filter(pub_date__lt=datetime.now())
        if self.value() == 'Unpublished':
            return queryset.filter(pub_date__gte=datetime.now())

# @admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # è la view per la lista degli ogetti Author
    def changelist_view(self, request, extra_context=None):
        # Aggregate new authors per day
        chart_data = (
            Author.objects.annotate(date=TruncDay("updatedDate"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        print("Json %s" % as_json)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

    # questa è la vista per la pagina di EDIT della singola istanza di Author
    def change_view(self, request, object_id, form_url='', extra_context=None):
        nbQuestion = Question.objects.filter(refAuthor=object_id).count()
        response_data = [nbQuestion]

        extra_context = extra_context or {}

        # Serialize and attach the chart data to the template contexz
        as_json = json.dumps(response_data, cls=DjangoJSONEncoder)
        extra_context = extra_context or {"nbQuestion": as_json}
        return super().change_view(request, object_id, form_url, extra_context=extra_context, )

    empty_value_display = 'Unknown'
    fieldsets = [
        ("Author Info", {'fields': ['name','createdDate','updatedDate']}),
    ]
    list_display = ('name', 'createdDate', 'updatedDate',)
    list_per_page = 20

    search_fields = ('name',) #serve anche per fare autocomplete in edit dalle classi che hanno Authore come ForeignKey
    readonly_fields = ('createdDate', 'updatedDate',)
    inlines = [QuestionInline,]

    def save_model(self, request, obj, form, change):
        print("Author saved by user '%s'" % request.user)
        super().save_model(request, obj, form, change)

    # override data sent to display
    def get_queryset(self, request):
        qs = super(AuthorAdmin, self).get_queryset(request)
        # return qs.filter(name__startswith='j')
        return qs



# @admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    class QuestionPublishedListFilter(admin.SimpleListFilter):
        # Human-readable title which will be displayed in the
        # right admin sidebar just above the filter options.
        title = ('Published questions')
        # Parameter for the filter that will be used in the URL query.
        parameter_name = 'pub_date'

        def lookups(self, request, model_admin):
            """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
            return (
                ('Published', ('Published questions')),
                ('Unpublished', ('Unpublished questions')),
            )

        def queryset(self, request, queryset):
            """
            Returns the filtered queryset based on the value
            provided in the query string and retrievable via
            `self.value()`.
            """
            if self.value() == 'Published':
                return queryset.filter(pub_date__lt=datetime.now(tz=timezone.get_default_timezone()))
            if self.value() == 'Unpublished':
                return queryset.filter(pub_date__gte=datetime.now(tz=timezone.get_default_timezone()))


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

    list_filter = (
                    QuestionPublishedListFilter ,  # custom filter
                    'refAuthor',
                   )
    autocomplete_fields = ['refAuthor']
    # OPPURE
    #raw_id_fields = ('refAuthor',)

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

    # custom action
    def make_published(modeladmin, request, queryset):
        queryset.update(pub_date=datetime.now(tz=timezone.get_default_timezone()) - timedelta(days=1))

    # per salvare i campi in un csv (ma non i campi manytomany o ForeignKey
    def export_to_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; \
            filename={}.csv'.format(opts.verbose_name)
        writer = csv.writer(response)
        fields = [field for field in opts.get_fields()
                  if not field.many_to_many and not field.one_to_many]
        # Write a first row with header information
        writer.writerow([field.verbose_name for field in fields])
        # Write data rows
        for obj in queryset:
            data_row = []
            for field in fields:
                value = getattr(obj, field.name)
                if isinstance(value, datetime):
                    value = value.strftime('%d/%m/%Y %H:%M')
                data_row.append(value)
            writer.writerow(data_row)
        return response

    export_to_csv.short_description = 'Export to CSV'

    #custom action che manda su una view e poi esegue l'azione con l'input che arriav da quella pagina
    # in realtà è semplicemente una View usata come action
    def make_published_custom(self, request, queryset):
        if 'apply' in request.POST:
            # The user clicked submit on the intermediate form.
            # # Perform our update action:
            queryset.update(pub_date=datetime.now(tz=timezone.get_default_timezone()) - timedelta(days=1))
            # Redirect to our admin view after our update has
            # completed with a nice little info message saying
            # our models have been updated:
            self.message_user(request,
                              "Changed to published on {} questions".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        return render(request, 'admin/custom_makepublished.html', context={'questions': queryset})

    actions = [make_published,export_to_csv,make_published_custom]

    make_published.short_description = "Mark selected questions as published"


# Register your models here.

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_text','votes','createdDate', 'updatedDate',)
    list_filter = ('question__refAuthor','question',)
    ordering = ('-createdDate',)
    list_per_page = 20
    search_fields = ('choice_text', 'question__refAuthor__name', 'question__question_text',)
    
    #performances
    list_select_related = ('question', 'question__refAuthor',)


# @admin.register(AuthorClone) STO USANDO CUSTOM SITE
class AuthorCloneAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Author information", {'fields': ['name','createdDate','updatedDate']}), # se metto altri campi poi non ppsso cambiarli nel clone
                                                # se nell'originale admin non erano in lista dei field / fieldsets
    ]
    list_display = ('name','createdDate','updatedDate',)
    readonly_fields = ('createdDate','updatedDate',)
    search_fields = ('name',)

from django.contrib.admin import AdminSite

## Custom admin site
class MyUltimateAdminSite(AdminSite):
    site_header = 'My Django Admin Ultimate Guide'
    site_title = 'My Django Admin Ultimate Guide Administration'
    index_title = 'Welcome to my "sample_app"'

site = MyUltimateAdminSite()

# admin.site.register(Choice,ChoiceAdmin)
# admin.site.register(QuestionSummary)

site.register(Author,AuthorAdmin)
site.register(Question,QuestionAdmin)
site.register(Choice,ChoiceAdmin)
site.register(Group)
site.register(User)
