from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import random
from django.http import Http404
from .models import Question, Tag, Answer


# Глобальная переменная для хранения вопросов
GLOBAL_QUESTIONS = []

def generate_random_questions(n = 100):
    #Генерация случйных вопросов
    titles = [
        "Как работает Django ORM?",
        "Почему Python считается интерпретируемым языком?",
        "Что такое middleware в Django?",
        "Как работает система шаблонов Django?",
        "Какие отличия между List и Tuple в Python?",
        "Как сделать авторизацию пользователя?",
        "Как подключить Bootstrap к Django?",
        "Что такое контекст шаблона?",
        "Как работает render() в Django?",
        "Как добавить статику в Django проект?"
    ]

    tags_combinations = [
        ['python', 'django', 'orm'],
        ['python', 'programming', 'basics'],
        ['django', 'web', 'middleware'],
        ['django', 'templates', 'frontend'],
        ['python', 'list', 'tuple', 'data-structures'],
        ['django', 'authentication', 'security'],
        ['bootstrap', 'css', 'frontend'],
        ['django', 'context', 'templates'],
        ['django', 'views', 'render'],
        ['django', 'static', 'files']
    ]

    answers_templates = [
        "Отличный вопрос! Обычно это делается с помощью встроенных инструментов Django.",
        "Можно использовать документацию Django — там есть подробный пример.",
        "Попробуйте использовать команду `python manage.py makemigrations` и `migrate`.",
        "Я бы предложил посмотреть в официальную документацию Python.",
        "Убедитесь, что в настройках `INSTALLED_APPS` указано нужное приложение.",
        "Это связано с тем, как Django управляет ORM транзакциями."
    ]

    authors = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]

    questions = []
    for i in range(1, n + 1):
        #Генерируем случайное количество ответов
        num_answers = random.randint(0,5)
        answers = []
        for j in range (num_answers):
            answers.append({
                "id": j + 1,
                "content": random.choice(answers_templates),
                "author": random.choice(authors),
                "created_at": f"{random.randint(1, 59)} мин.",
                "votes": random.randint(0, 5),
                "answer_avatar" : "components/user-profile-pic.webp"
            })

        questions.append({
            "id" : i,
            "title" : random.choice(titles),
            "description" : f"Это случайно сгенерированный вопрос №{i}."
                            f"Значение случайного числа: {random.randint(1, 999)}."
                            f"Описание предназначено для теста пагинации.",
            "votes" : random.randint(1,30),
            "answers_count" : num_answers,
            "tags" : random.choice(tags_combinations),
            "author_avatar" : "components/user-profile-pic.webp",
            "created_at": f"{random.randint(20, 50)} с.",
            "answers" : answers

        })
    return questions

def index(request):
    global GLOBAL_QUESTIONS

    #Генерация 50 слуачных вопросов
    if not GLOBAL_QUESTIONS:
        GLOBAL_QUESTIONS = generate_random_questions(50)

    sort_type = request.GET.get('sort', 'new')

    if sort_type == 'hot':
        questions_to_show = sorted(GLOBAL_QUESTIONS, key=lambda x: x["votes"], reverse=True)
    else:
        questions_to_show = sorted(GLOBAL_QUESTIONS, key=lambda x: x["id"], reverse=True)

    paginator = Paginator(questions_to_show, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj' : page_obj,
        'current_sort': sort_type,  # передаем текущий тип сортировки в шаблон
    }
    
    return render(request, "index.html", context)


def question_detail(request, question_id):  # ← исправлено: question_id
    global GLOBAL_QUESTIONS
    
    # Ищем вопрос в наших данных
    question = None
    for q in GLOBAL_QUESTIONS:
        if q['id'] == question_id:
            question = q
            break
    
    # Если вопрос не найден - вызываем 404 ошибку
    if not question:
        raise Http404("Вопрос не найден")  # ← ИСПРАВЛЕНО
    
    context = {
        'question': question,
        'answers': question.get("answers", [])
    }

    return render(request, 'question.html', context)


def questions_by_tag(request, tag_name):
    questions_with_tag=[]
    for question in GLOBAL_QUESTIONS:
        if tag_name in question['tags']:
            questions_with_tag.append(question)
    
    # Сортируем по дате (новые первыми)
    questions_with_tag.sort(key=lambda x: x['id'], reverse=True)

    paginator = Paginator(questions_with_tag, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj' : page_obj,
        'tag_name' : tag_name,
        'questions_count' : len(questions_with_tag)
    }

    return render(request, 'questions_by_tag.html', context)



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


def user_profile(request, username):
    """Страница профиля пользователя (заглушка)"""
    # Пока просто заглушка, потом заменим на реальные данные из БД
    context = {
        'username' : username,
        'user_data' : {
            'rating' : 205,
            'questions_count' : 45,
            'answers_count' : 113,
            'member_since' : '2021' 
        }
    }

    return render(request, 'user_profile.html', context)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_400(request, exception):
    return render(request, '400.html', status=400)

def custom_500(request):
    return render(request, '500.html', status=500)


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def index(request):
    sort_type = request.GET.get('sort', 'new')  # получаем параметр сортировки
    
    if sort_type == 'hot':
        questions = Question.objects.best_questions()
    else:
        questions = Question.objects.new_questions()
    
    page_obj = paginate(questions, request)
    
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'current_sort': sort_type
    })

def hot_questions(request):
    questions = Question.objects.best_questions()
    page_obj = paginate(questions, request)
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'current_sort': 'hot'
    })

def questions_by_tag(request, tag_name):
    """Вопросы по тегу"""
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.questions_by_tag(tag_name)
    page_obj = paginate(questions, request)
    
    context = {
        'page_obj': page_obj,
        'tag': tag,  # ← передаем объект тега, а не только имя
        'questions_count': questions.count()
    }
    return render(request, 'questions_by_tag.html', context)

def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question).order_by('-rating', '-created_at')
    page_obj = paginate(answers, request, per_page=5)
    return render(request, 'question.html', {
        'question': question,
        'page_obj': page_obj
    })