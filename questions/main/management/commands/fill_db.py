from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from main.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from django.db import transaction
from django.db.models import Max
from django.db.models import Sum, Count

class Command(BaseCommand):
    help = 'Fill database with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Fill ratio')
    
    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        
        self.stdout.write(f'🚀 Starting to fill database with ratio: {ratio}')
        self.stdout.write(f'📊 Expected: Users: {ratio}, Questions: {ratio * 10}, Answers: {ratio * 100}, Tags: {ratio}, Likes: {ratio * 200}')
        
        # Очищаем базу перед заполнением
        self.stdout.write('🗑️ Clearing existing data...')
        with transaction.atomic():
            AnswerLike.objects.all().delete()
            QuestionLike.objects.all().delete()
            Answer.objects.all().delete()
            Question.objects.all().delete()
            # Удаляем связи many-to-many перед удалением тегов
            Question.tags.through.objects.all().delete()
            Tag.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Database cleared'))
        
        with transaction.atomic():
            # Создаем пользователей и профили пачками
            self.stdout.write(f'👥 Creating {ratio} users and profiles...')
            users = []
            
            for i in range(ratio):
                username = f"user_{i}_{fake.user_name()}"
                users.append(User(
                    username=username,
                    email=fake.email(),
                    password='password123'
                ))
                
                if (i + 1) % 1000 == 0:
                    self.stdout.write(f'   Prepared {i + 1}/{ratio} users')
            
            # Bulk
            User.objects.bulk_create(users, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(users)} users'))
            
            # Получаем ID созданных пользователей
            user_ids = list(User.objects.values_list('id', flat=True))
            
            # Создаем профили
            profiles = []
            for user_id in user_ids:
                profiles.append(Profile(user_id=user_id))
            
            Profile.objects.bulk_create(profiles, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(profiles)} profiles'))
            
            # Создаем теги пачками
            self.stdout.write(f'🏷️ Creating {ratio} tags...')
            tags = []
            tag_names = set()
            
            for i in range(ratio):
                tag_name = f"tag_{i}_{fake.word()}"
                # Гарантируем уникальность имен
                while tag_name in tag_names:
                    tag_name = f"tag_{i}_{fake.word()}_{random.randint(1000, 9999)}"
                tag_names.add(tag_name)
                
                tags.append(Tag(name=tag_name))
                
                if (i + 1) % 1000 == 0:
                    self.stdout.write(f'   Prepared {i + 1}/{ratio} tags')
            
            Tag.objects.bulk_create(tags, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(tags)} tags'))
            
            # Получаем ID созданных тегов
            tag_ids = list(Tag.objects.values_list('id', flat=True))
            
            # Создаем вопросы пачками
            self.stdout.write(f'❓ Creating {ratio * 10} questions...')
            questions = []
            
            for i in range(ratio * 10):
                questions.append(Question(
                    title=fake.sentence()[:200],
                    content=fake.text(max_nb_chars=1000),
                    author_id=random.choice(user_ids),
                    rating=random.randint(0, 100)
                ))
                
                if (i + 1) % 5000 == 0:
                    self.stdout.write(f'   Prepared {i + 1}/{ratio * 10} questions')
            
            # Bulk
            Question.objects.bulk_create(questions, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(questions)} questions'))
            
            # Получаем ID созданных вопросов
            question_ids = list(Question.objects.values_list('id', flat=True))
            
            # Добавляем теги к вопросам (many-to-many)
            self.stdout.write('🔗 Adding tags to questions...')
            question_tag_relations = []
            
            for question_id in question_ids:
                # 1-3 случайных тега на вопрос
                num_tags = random.randint(1, min(3, len(tag_ids)))
                for tag_id in random.sample(tag_ids, num_tags):
                    question_tag_relations.append(Question.tags.through(
                        question_id=question_id,
                        tag_id=tag_id
                    ))
            
            Question.tags.through.objects.bulk_create(question_tag_relations, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f'✅ Added {len(question_tag_relations)} tag relations'))
            
            # Создаем ответы пачками
            self.stdout.write(f'💬 Creating {ratio * 100} answers...')
            answers = []
            
            for i in range(ratio * 100):
                answers.append(Answer(
                    content=fake.text(max_nb_chars=500),
                    author_id=random.choice(user_ids),
                    question_id=random.choice(question_ids),
                    rating=random.randint(0, 50)
                ))
                
                if (i + 1) % 10000 == 0:
                    self.stdout.write(f'   Prepared {i + 1}/{ratio * 100} answers')
            
            Answer.objects.bulk_create(answers, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(answers)} answers'))
            
            # Получаем ID созданных ответов
            answer_ids = list(Answer.objects.values_list('id', flat=True))
            
            # Создаем лайки для вопросов пачками
            self.stdout.write(f'👍 Creating {ratio * 200} total likes...')
            question_likes = []
            answer_likes = []
            
            # Лайки для вопросов (~50%)
            question_likes_target = ratio * 100
            question_like_combinations = set()
            
            # Получаем информацию об авторах вопросов
            question_authors = {q.id: q.author_id for q in Question.objects.only('id', 'author_id')}
            
            while len(question_likes) < question_likes_target:
                user_id = random.choice(user_ids)
                question_id = random.choice(question_ids)
                
                # Проверяем, не автор ли вопроса и не дубликат
                if user_id != question_authors[question_id] and (user_id, question_id) not in question_like_combinations:
                    question_like_combinations.add((user_id, question_id))
                    question_likes.append(QuestionLike(
                        user_id=user_id,
                        question_id=question_id,
                        value=random.choice([1, -1])
                    ))
                
                if len(question_likes) % 5000 == 0 and len(question_likes) > 0:
                    self.stdout.write(f'   Prepared {len(question_likes)}/{question_likes_target} question likes')
            
            if question_likes:
                QuestionLike.objects.bulk_create(question_likes, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(question_likes)} question likes'))
            
            # Лайки для ответов (~50%)
            answer_likes_target = ratio * 100
            answer_like_combinations = set()
            
            # Получаем информацию об авторах ответов
            answer_authors = {a.id: a.author_id for a in Answer.objects.only('id', 'author_id')}
            
            while len(answer_likes) < answer_likes_target:
                user_id = random.choice(user_ids)
                answer_id = random.choice(answer_ids)
                
                # Проверяем, не автор ли ответа и не дубликат
                if user_id != answer_authors[answer_id] and (user_id, answer_id) not in answer_like_combinations:
                    answer_like_combinations.add((user_id, answer_id))
                    answer_likes.append(AnswerLike(
                        user_id=user_id,
                        answer_id=answer_id,
                        value=random.choice([1, -1])
                    ))
                
                if len(answer_likes) % 5000 == 0 and len(answer_likes) > 0:
                    self.stdout.write(f'   Prepared {len(answer_likes)}/{answer_likes_target} answer likes')
            
            if answer_likes:
                AnswerLike.objects.bulk_create(answer_likes, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(answer_likes)} answer likes'))

            for user in User.objects.all():

                profile = Profile.objects.get(user=user)

                question_rating = Question.objects.filter(
                    author=user
                ).aggregate(total=Sum('rating'))['total'] or 0

                answer_rating = Answer.objects.filter(
                    author=user
                ).aggregate(total=Sum('rating'))['total'] or 0
                
                answers_count = Answer.objects.filter(author=user).count()
                
                profile.rating = question_rating + answer_rating
                profile.answers_count = answers_count
                profile.save()

        
        # Финальная статистика
        self.stdout.write(self.style.SUCCESS('🎉 Database filled successfully!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Final stats:'))
        self.stdout.write(self.style.SUCCESS(f'   👥 Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   🏷️ Tags: {Tag.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   ❓ Questions: {Question.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   💬 Answers: {Answer.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   👍 Question likes: {QuestionLike.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   👍 Answer likes: {AnswerLike.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   👍 Total likes: {QuestionLike.objects.count() + AnswerLike.objects.count()}'))