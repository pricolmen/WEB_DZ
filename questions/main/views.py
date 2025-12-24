from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from .models import Question, Tag, Answer, Profile
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm,
    ProfileEditForm,
    QuestionForm,
    AnswerForm
)

# Утилитарная функция для пагинации
def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

# Главная страница
def index(request):
    sort_type = request.GET.get('sort', 'new')
    
    if sort_type == 'hot':
        questions = Question.objects.best_questions()
    else:
        questions = Question.objects.new_questions()
    
    page_obj = paginate(questions, request)
    
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'current_sort': sort_type
    })

# Популярные вопросы
def hot_questions(request):
    questions = Question.objects.best_questions()
    page_obj = paginate(questions, request)
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'current_sort': 'hot'
    })

# Вопросы по тегу
def questions_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.questions_by_tag(tag_name)
    page_obj = paginate(questions, request)
    
    context = {
        'page_obj': page_obj,
        'tag': tag,
        'questions_count': questions.count()
    }
    return render(request, 'questions_by_tag.html', context)

# Страница вопроса
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Получаем ВСЕ ответы на вопрос
    all_answers = Answer.objects.filter(question=question).order_by('-rating', '-created_at')
    
    # Пагинируем ответы (например, по 10 на страницу)
    page_obj = paginate(all_answers, request, per_page=10)
    
    # Форма для ответа (только для авторизованных)
    answer_form = AnswerForm() if request.user.is_authenticated else None
    
    return render(request, 'question.html', {
        'question': question,
        'page_obj': page_obj,  # Теперь это пагинированные ответы
        'answer_form': answer_form
    })

# Регистрация
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

# Вход
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    # Получаем URL для редиректа после входа
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                
                # Редирект на next или главную
                next_url = request.POST.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('index')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {
        'form': form,
        'next': next_url
    })

# Выход
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    # Возвращаем на ту же страницу, откуда вышли
    return redirect(request.META.get('HTTP_REFERER', 'index'))

# Просмотр профиля
@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    # Получаем вопросы и ответы пользователя
    user_questions = Question.objects.filter(author=request.user).order_by('-created_at')[:10]
    user_answers = Answer.objects.filter(author=request.user).order_by('-created_at')[:10]
    
    context = {
        'profile': profile,
        'user_questions': user_questions,
        'user_answers': user_answers,
    }
    
    return render(request, 'profile.html', context)

# Редактирование профиля
@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(
            request.POST, 
            request.FILES, 
            instance=profile, 
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile_view')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})

# Публичный профиль пользователя
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    
    # Вопросы пользователя
    user_questions = Question.objects.filter(author=user).order_by('-created_at')[:20]
    user_answers = Answer.objects.filter(author=user).order_by('-created_at')[:20]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'user_questions': user_questions,
        'user_answers': user_answers,
    }
    
    return render(request, 'user_profile.html', context)


@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            tags = form.cleaned_data['tags']
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
            
            messages.success(request, 'Вопрос успешно добавлен!')
            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})

# Добавление ответа
@login_required  
def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            
            messages.success(request, 'Ответ добавлен!')
            
            # Простой редирект на страницу вопроса
            # Новый ответ будет на первой странице (самые свежие/с высоким рейтингом)
            return HttpResponseRedirect(
                f"{reverse('question', args=[question_id])}#answer-{answer.id}"
            )
    
    return redirect('question', question_id=question_id)

def custom_404(request, exception):
    return render(request, '404.html', {"exception": exception}, status=404)

def custom_400(request, exception):
    return render(request, '400.html', {"exception": exception}, status=400)

def custom_500(request):
    return render(request, '500.html', status=500)