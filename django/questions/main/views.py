from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    questions = [
        {
            'id': 1,
            'title': 'How to build a mean peak?',
            'description': 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Ullam nulla laboriosam, tempore libero mollitia sunt omnis odit tenetur totam quam veritatis, sint atque facere laborum aperiam sapiente culpa dolorem vero.',
            'votes': 5,
            'answers_count': 3,
            'tags': ['bender', 'black-jack'],
            'author_avatar': 'components/user-profile-pic.webp'
        },
        {
            'id': 2,
            'title': 'Как настроить Django с PostgreSQL?',
            'description': 'Пытаюсь настроить Django с PostgreSQL, но получаю ошибку подключения. В settings.py я указал следующие настройки...',
            'votes': 8,
            'answers_count': 2,
            'tags': ['python', 'django', 'postgresql'],
            'author_avatar': 'components/user-profile-pic.webp'
        },
        {
            'id': 3,
            'title': 'Лучшие практики работы с Bootstrap 5',
            'description': 'Какие есть лучшие практики при работе с Bootstrap 5? Особенно интересует кастомизация компонентов...',
            'votes': 12,
            'answers_count': 5,
            'tags': ['bootstrap', 'css', 'frontend'],
            'author_avatar': 'components/user-profile-pic.webp'
        }
    ]

    context = {
        'questions': questions
    }
    
    return render(request, "index.html", context)


def question_detail(request, question_id):  # ← исправлено: question_id
    questions_data = {
        1: {
            'title': 'How to build a mean peak?',
            'description': 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Ullam nulla laboriosam, tempore libero mollitia sunt omnis odit tenetur totam quam veritatis, sint atque facere laborum aperiam sapiente culpa dolorem vero.',
            'votes': 5,
            'answers_count': 3,
            'tags': ['bender', 'black-jack'],
            'author_avatar': 'components/user-profile-pic.webp'
        },
        2: {
            'title': 'Как настроить Django с PostgreSQL?',
            'description': 'Пытаюсь настроить Django с PostgreSQL, но получаю ошибку подключения. В settings.py я указал следующие настройки...',
            'votes': 8,
            'answers_count': 2,
            'tags': ['python', 'django', 'postgresql'],
            'author_avatar': 'components/user-profile-pic.webp'
        },
        3: {
            'title': 'Лучшие практики работы с Bootstrap 5',
            'description': 'Какие есть лучшие практики при работе с Bootstrap 5? Особенно интересует кастомизация компонентов...',
            'votes': 12,
            'answers_count': 5,
            'tags': ['bootstrap', 'css', 'frontend'],
            'author_avatar': 'components/user-profile-pic.webp'
        }
    }

    if question_id in questions_data:
        question_data = questions_data[question_id]
    else:
        question_data = {
            'title': f'Вопрос #{question_id}',
            'description': 'Этот вопрос еще не имеет описания. Будьте первым, кто добавит подробности!',
            'votes': 0,
            'answers_count': 0,
            'tags': ['general'],
        }

    question = {
        'id': question_id,
        'title': question_data['title'],
        'description': question_data['description'],
        'votes': question_data['votes'],
        'answers_count': question_data['answers_count'],
        'tags': question_data['tags'],
        'author_avatar': 'components/user-profile-pic.webp',
        'created_at': '2 часа назад'
    }

    context = {
        'question' : question
    }

    return render(request, 'question.html', context)


@login_required
def ask_question(request):
    if request.method == 'POST':
        # Здесь будет обработка формы
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags = request.POST.get('tags')
        
        # Временный редирект на главную
        return redirect('index')
    
    return render(request, 'ask.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

# Вход
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('index')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

# Выход
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')

# Профиль пользователя
@login_required
def profile(request):
    context = {
        'user': request.user
    }
    return render(request, 'profile.html', context)

def signup(request):
    return render(request, 'signup.html')

def login_view(request):
    return render(request, 'login.html')

def profile(request):
    return render(request, 'profile.html')

def ask_question(request):
    return render(request, 'ask.html')
