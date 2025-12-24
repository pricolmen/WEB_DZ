# Ваш файл с sidebar_data
from django.contrib.auth.models import User
from main.models import Tag, Profile

def sidebar_data(request):
    # Популярные теги (первые 10)
    popular_tags = Tag.objects.all()[:10]
    
    # Лучшие пользователи с рейтингом
    # Используем select_related для оптимизации запросов
    best_profiles = Profile.objects.select_related('user') \
        .order_by('-rating')[:5]
    
    # Подготавливаем данные для шаблона
    best_users_data = []
    for profile in best_profiles:
        best_users_data.append({
            'id': profile.user.id,
            'username': profile.user.username,
            'rating': profile.rating,
            'answers_count': profile.answers_count,
            'avatar': profile.avatar,  # если нужен аватар
        })
    
    return {
        'popular_tags': popular_tags,
        'best_users': best_users_data,
    }