from django.contrib import admin
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar']
    search_fields = ['user__username']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'created_at']
    list_filter = ['created_at', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']  # удобный выбор тегов

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['author', 'question', 'rating', 'is_correct', 'created_at']
    list_filter = ['is_correct', 'created_at']
    search_fields = ['content']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value', 'created_at']
    list_filter = ['value', 'created_at']

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'value', 'created_at']
    list_filter = ['value', 'created_at']