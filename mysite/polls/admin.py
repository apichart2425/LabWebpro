from django.contrib import admin
from django.contrib.auth.models import Permission

from polls.models import Poll, Question, Choice, Comment

admin.site.register(Permission)

class QuestionInLine(admin.StackedInline):
    model = Question

class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 1

class PollAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date', 'del_flag']

    list_filter = ['start_date', 'end_date', 'del_flag', 'title']
    search_fields = ['title']

    fieldsets = [
        (None, {'fields': ['title', 'del_flag']}),
        ("Active Duration", {'fields': ['start_date', 'end_date'], 'classes': ['collapse']})
    ]

    inlines = [QuestionInLine]

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'value']
    list_per_page = 10

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll', 'text']
    list_per_page =  15

    inlines = [ChoiceInLine]

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'email', 'tel', 'poll']
    search_fields = ['title']
    list_filter = ['poll_id']


admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Comment,CommentAdmin)
# Register your models here.
