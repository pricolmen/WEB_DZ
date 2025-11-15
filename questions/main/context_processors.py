from django.contrib.auth.models import User
from main.models import Tag

def sidebar_data(request):
    # Популярные теги (первые 10)
    popular_tags = Tag.objects.all()[:10]
    
    # Лучшие пользователи (первые 5)
    best_users = User.objects.all()[:5]
    
    return {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }