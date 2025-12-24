# management/commands/fix_ratings.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile, Question, Answer
from django.db.models import Sum, Count

class Command(BaseCommand):
    help = 'Update user ratings in profiles based on existing questions and answers'
    
    def handle(self, *args, **options):
        self.stdout.write('🔄 Updating user ratings in profiles...')
        
        total_users = User.objects.count()
        processed = 0
        
        for user in User.objects.all():
            # Получаем профиль
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Считаем рейтинг вопросов
            question_rating = Question.objects.filter(
                author=user
            ).aggregate(total=Sum('rating'))['total'] or 0
            
            # Считаем рейтинг ответов
            answer_rating = Answer.objects.filter(
                author=user
            ).aggregate(total=Sum('rating'))['total'] or 0
            
            # Считаем количество ответов
            answers_count = Answer.objects.filter(author=user).count()
            
            # Обновляем профиль
            profile.rating = question_rating + answer_rating
            profile.answers_count = answers_count
            profile.save()
            
            processed += 1
            
            if processed % 100 == 0:
                self.stdout.write(f'   Processed {processed}/{total_users} users')
        
        # Показываем результат
        self.stdout.write('\n🏆 Top 5 users by rating:')
        top_users = Profile.objects.select_related('user').order_by('-rating')[:5]
        for i, profile in enumerate(top_users, 1):
            self.stdout.write(f'   {i}. {profile.user.username}: rating={profile.rating}, answers={profile.answers_count}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully updated ratings for {processed} users'))