from django.contrib import admin

from .models import Question, Tag, Answer


# class QaAdminSite(admin.AdminSite):
#     site_header = "Hasker Q&A Administration"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["title", "question_text", "tags"]}),
        ("Date information", {"fields": ["created"]}),
    ]
    inlines = [AnswerInline]
    list_display = ["title", "created", "was_created_recently"]
    list_filter = ["created"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)

admin.site.register(Tag)

admin.site.register(Answer)
