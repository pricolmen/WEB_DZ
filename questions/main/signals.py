# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль только при создании пользователя"""
    if created:
        Profile.objects.get_or_create(user=instance)  # Используем get_or_create для безопасности

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Если профиля почему-то нет, создаем
        Profile.objects.get_or_create(user=instance)