from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    rating = models.IntegerField(default=0)  # Добавляем рейтинг
    answers_count = models.IntegerField(default=0)  # Добавляем количество ответов
    nickname = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"Profile of {self.user.username} - Rating: {self.rating}"
    
    def update_rating(self):
        answers_rating = Answer.objects.filter(author=self.user).aggregate(
            total=models.Sum('rating')
        )['total'] or 0

        self.answers_count = Answer.objects.filter(author=self.user).count()
        
        self.rating = answers_rating
        self.save()
        return self.rating
    
    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.user.username
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class QuestionManager(models.Manager):
    def new_questions(self):
        return self.order_by('-created_at')
    
    def best_questions(self):
        return self.order_by('-rating')
    
    def questions_by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-created_at')

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)
    
    objects = QuestionManager()
    
    def __str__(self):
        return self.title
    
    def update_rating(self):
        likes = QuestionLike.objects.filter(question=self)
        self.rating = sum(like.value for like in likes)
        self.save()
    
    def get_absolute_url(self):
        return f"/question/{self.id}/"

class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    def update_rating(self):
        likes = AnswerLike.objects.filter(answer=self)
        self.rating = sum(like.value for like in likes)
        self.save()

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'question']  # один пользователь - один лайк на вопрос
    
    def clean(self):
        if self.user == self.question.author:
            raise ValidationError("You cannot like your own question")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.question.update_rating()

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'answer']  # один пользователь - один лайк на ответ
    
    def clean(self):
        if self.user == self.answer.author:
            raise ValidationError("You cannot like your own answer")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.answer.update_rating()



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Question)
@receiver(post_save, sender=Answer)
@receiver(post_delete, sender=Question)
@receiver(post_delete, sender=Answer)
@receiver(post_save, sender=QuestionLike)
@receiver(post_save, sender=AnswerLike)
@receiver(post_delete, sender=QuestionLike)
@receiver(post_delete, sender=AnswerLike)
def update_user_profile_rating(sender, instance, **kwargs):
    from django.db.models import Sum
    
    # Определяем пользователя для обновления
    if hasattr(instance, 'author'):
        user = instance.author
    elif isinstance(instance, QuestionLike):
        user = instance.question.author
    elif isinstance(instance, AnswerLike):
        user = instance.answer.author
    else:
        return
    
    # Обновляем рейтинг
    try:
        profile = Profile.objects.get(user=user)
        
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
        
    except Profile.DoesNotExist:
        # Создаем профиль, если его нет
        Profile.objects.create(user=user)