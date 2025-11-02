from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Student(models.Model):
    familya = models.CharField(max_length=100)
    ism = models.CharField(max_length=100)
    group = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    is_online = models.BooleanField(default=False)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.familya} {self.ism}"
    
    class Meta:
        db_table = 'students'

class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit = models.IntegerField(help_text="Daqiqalarda")  # minutes
    max_score = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'tests'

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'questions'
        ordering = ['order']

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'answers'

class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    answers_data = models.JSONField(default=dict)  # Store student's answers
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'test_results'

class StudentLogin(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='login_info')
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.username} - {self.student.familya} {self.student.ism}"
    
    class Meta:
        db_table = 'student_logins'

class StudentActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Tizimga kirish'),
        ('test_start', 'Test boshlash'),
        ('test_complete', 'Test yakunlash'),
        ('profile_update', 'Profil yangilash'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_activities'