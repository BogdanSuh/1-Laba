from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    expires_at = models.DateTimeField('Время окончания', null=True, blank=True)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def is_active(self):
        """Активен ли вопрос (по времени жизни)."""
        return self.expires_at is None or timezone.now() < self.expires_at

    def total_votes(self):
        """Всего голосов."""
        return sum(choice.votes for choice in self.choice_set.all())

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    """Чтобы пользователь мог голосовать только один раз."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'question')
