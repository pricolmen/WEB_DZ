# main/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Profile, Question, Answer, Tag

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nickname = forms.CharField(
        max_length=50, 
        required=False, 
        label='Псевдоним',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем Bootstrap классы ко всем полям
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Проверка на уникальность логина
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        
        # Дополнительные проверки логина (опционально)
        if len(username) < 3:
            raise ValidationError("Логин должен содержать минимум 3 символа.")
        
        # Проверка на допустимые символы
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError(
                "Логин может содержать только буквы, цифры и символы @/./+/-/_"
            )
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        
        # Проверка на уникальность email
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        
        # Проверка формата email (опционально, так как EmailField уже делает это)
        if not email:
            raise ValidationError("Email обязателен для заполнения.")
        
        return email
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname', '').strip()
        
        if nickname:
            # Проверяем, не занят ли никнейм другим пользователем
            if Profile.objects.filter(nickname__iexact=nickname).exists():
                raise ValidationError("Этот псевдоним уже занят.")
            
            if len(nickname) < 2:
                raise ValidationError("Псевдоним должен содержать минимум 2 символа.")
        
        return nickname
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Дополнительные проверки между полями
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()  # Сохраняем email в нижнем регистре
        
        if commit:
            user.save()
            
            # Создаем или обновляем профиль
            profile, created = Profile.objects.get_or_create(user=user)
            nickname = self.cleaned_data.get('nickname', '').strip()
            if nickname:
                profile.nickname = nickname
            profile.save()
        
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Позволяем логин по email
            if '@' in username:
                email = username.strip().lower()
                # Ищем пользователя по email (без учета регистра)
                users = User.objects.filter(email__iexact=email)
                
                if users.exists():
                    # Берем первого пользователя с таким email
                    user = users.first()
                    username = user.username
                else:
                    raise forms.ValidationError(
                        "Пользователь с таким email не найден."
                    )
        return super().clean()

class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Логин', 
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']
        labels = {
            'nickname': 'Псевдоним',
            'avatar': 'Аватар',
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['username'].initial = self.user.username
            
        # Добавляем Bootstrap классы
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        
        # Проверяем, не занят ли email другим пользователем
        if self.user and User.objects.filter(email__iexact=email).exclude(id=self.user.id).exists():
            raise ValidationError("Этот email уже используется другим пользователем.")
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Проверяем, не занят ли логин другим пользователем
        if self.user and User.objects.filter(username__iexact=username).exclude(id=self.user.id).exists():
            raise ValidationError("Этот логин уже занят.")
        
        # Дополнительные проверки
        if len(username) < 3:
            raise ValidationError("Логин должен содержать минимум 3 символа.")
        
        return username
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname', '').strip()
        
        if nickname:
            # Проверяем, не занят ли никнейм другим пользователем
            if self.user and Profile.objects.filter(
                nickname__iexact=nickname
            ).exclude(user=self.user).exists():
                raise ValidationError("Этот псевдоним уже занят.")
            
            if len(nickname) < 2:
                raise ValidationError("Псевдоним должен содержать минимум 2 символа.")
        
        return nickname
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Обновляем данные пользователя
        if self.user:
            self.user.email = self.cleaned_data['email']
            self.user.username = self.cleaned_data['username']
            
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        
        return profile

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        help_text='Введите теги через запятую',
        required=True
    )
    
    class Meta:
        model = Question
        fields = ['title', 'content']
        labels = {
            'title': 'Заголовок',
            'content': 'Текст вопроса',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }
    
    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        if len(tags) > 5:
            raise forms.ValidationError("Максимум 5 тегов")
        
        if len(tags) == 0:
            raise forms.ValidationError("Добавьте хотя бы один тег")
        
        return tags

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': 'Ваш ответ',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите ваш ответ здесь...'}),
        }