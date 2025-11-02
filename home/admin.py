from django.contrib import admin
from .models import Student, Test, Question, Answer, TestResult, StudentActivity

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'familya', 'ism', 'group', 'is_online', 'login_attempts', 'created_at']
    list_filter = ['is_online', 'group', 'created_at']
    search_fields = ['familya', 'ism', 'group']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'time_limit', 'max_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'test', 'text', 'order']
    list_filter = ['test']
    search_fields = ['text']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'is_correct']
    list_filter = ['question__test', 'is_correct']
    search_fields = ['text']

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'test', 'score', 'total_questions', 'correct_answers', 'completed_at']
    list_filter = ['test', 'completed_at']
    search_fields = ['student__familya', 'student__ism', 'test__title']

@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'activity_type', 'details', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['student__familya', 'student__ism', 'details']