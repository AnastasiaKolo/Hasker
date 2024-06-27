""" Admin page for Q&A app """
from django.contrib import admin

from .models import Question, Tag, Answer


admin.site.register(Tag)

class AnswerInline(admin.TabularInline):
    """ Enables to view and edit corresponding answers on Question page """
    model = Answer
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """ Custom config for Question edit page in admin interface """
    fieldsets = [
        (None, {"fields": ["title", "question_text", "author", "tags"]}),
        ("Date information", {"fields": ["created"]}),
    ]
    inlines = [AnswerInline]
    list_display = ["title", "created", "author", "was_created_recently", "display_tags"]
    list_filter = ["created", "author"]
    search_fields = ["question_text"]
