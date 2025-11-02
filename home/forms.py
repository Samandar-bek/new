from django import forms
from .models import Student, StudentLogin, Test, Question, ChatMessage

class LoginForm(forms.Form):
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Familiyangizni kiriting',
            'required': True
        }),
        label="Familiya"
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ismingizni kiriting',
            'required': True
        }),
        label="Ism"
    )

class StudentLoginForm(forms.ModelForm):
    class Meta:
        model = StudentLogin
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'O\'quvchi logini',
                'required': True
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'O\'quvchi paroli',
                'required': True
            }),
        }

class AdminPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Parolni kiriting',
            'required': True
        }),
        label="Parol"
    )

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'time_limit']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Test nomi'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Test tavsifi'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Savol matni'}),
            'option_a': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Variant A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Variant B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Variant C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Variant D'}),
            'correct_answer': forms.Select(attrs={'class': 'form-input'}),
        }

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message_text']
        widgets = {
            'message_text': forms.TextInput(attrs={
                'class': 'chat-input',
                'placeholder': 'Xabar yozing...',
                'required': True
            }),
        }