from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from main.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

class Command(BaseCommand):
    help = 'Fill database with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Fill ratio')
    
    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        
        self.stdout.write(f'🚀 Starting to fill database with ratio: {ratio}')
        
        # Создаем пользователей и профили
        self.stdout.write(f'👥 Creating {ratio} users and profiles...')
        users = []
        for i in range(ratio):
            try:
                user = User.objects.create_user(
                    username=fake.user_name() + str(i),
                    email=fake.email(),
                    password='password123'
                )
                Profile.objects.create(user=user)
                users.append(user)
                
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'   Created {i + 1}/{ratio} users')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {i}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(users)} users'))
        
        # Создаем теги
        self.stdout.write(f'🏷️ Creating {ratio} tags...')
        tags = []
        for i in range(ratio):
            tag = Tag.objects.create(name=fake.word() + str(i))
            tags.append(tag)
            if (i + 1) % 10 == 0:
                self.stdout.write(f'   Created {i + 1}/{ratio} tags')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(tags)} tags'))
        
        # Создаем вопросы
        self.stdout.write(f'❓ Creating {ratio * 10} questions...')
        questions = []
        for i in range(ratio * 10):
            question = Question.objects.create(
                title=fake.sentence(),
                content=fake.text(),
                author=random.choice(users),
                rating=random.randint(0, 100)
            )
            # Добавляем случайные теги к вопросу
            question_tags = random.sample(tags, min(3, len(tags)))
            question.tags.set(question_tags)
            questions.append(question)
            
            if (i + 1) % 50 == 0:
                self.stdout.write(f'   Created {i + 1}/{ratio * 10} questions')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(questions)} questions'))
        
        # Создаем ответы
        self.stdout.write(f'💬 Creating {ratio * 100} answers...')
        answers = []
        for i in range(ratio * 100):
            answer = Answer.objects.create(
                content=fake.text(),
                author=random.choice(users),
                question=random.choice(questions),
                rating=random.randint(0, 50)
            )
            answers.append(answer)
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   Created {i + 1}/{ratio * 100} answers')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(answers)} answers'))
        
        # Создаем лайки для вопросов
        self.stdout.write(f'👍 Creating {ratio * 100} question likes...')
        question_likes_created = 0
        for i in range(ratio * 100):
            user = random.choice(users)
            question = random.choice(questions)
            
            # Проверяем, не автор ли пользователь вопроса
            if user != question.author:
                try:
                    QuestionLike.objects.create(
                        user=user,
                        question=question,
                        value=random.choice([1, -1])
                    )
                    question_likes_created += 1
                except:
                    pass  # Игнорируем если лайк уже существует
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   Created {question_likes_created}/{ratio * 100} question likes')
        
        # Создаем лайки для ответов
        self.stdout.write(f'👍 Creating {ratio * 100} answer likes...')
        answer_likes_created = 0
        for i in range(ratio * 100):
            user = random.choice(users)
            answer = random.choice(answers)
            
            # Проверяем, не автор ли пользователь ответа
            if user != answer.author:
                try:
                    AnswerLike.objects.create(
                        user=user,
                        answer=answer,
                        value=random.choice([1, -1])
                    )
                    answer_likes_created += 1
                except:
                    pass  # Игнорируем если лайк уже существует
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   Created {answer_likes_created}/{ratio * 100} answer likes')
        
        self.stdout.write(self.style.SUCCESS('🎉 Database filled successfully!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Final stats:'))
        self.stdout.write(self.style.SUCCESS(f'   👥 Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   🏷️ Tags: {Tag.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   ❓ Questions: {Question.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   💬 Answers: {Answer.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   👍 Question likes: {QuestionLike.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   👍 Answer likes: {AnswerLike.objects.count()}'))