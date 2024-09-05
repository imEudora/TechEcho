from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils import timezone

from answers.models import Answer
from questions.models import Question


class TeacherInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expertise = models.CharField(max_length=255)
    introduce = models.TextField(
        validators=[MinLengthValidator(100), MaxLengthValidator(500)]
    )
    nickname = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    schedule = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user.is_teacher = True
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nickname or self.user.username} - {self.expertise}"

    def get_questions(self):
        return Question.objects.filter(user=self.user)

    def get_answers(self):
        return Answer.objects.filter(user=self.user)
