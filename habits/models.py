from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users.models import User

NULLABLE = {"blank": True, "null": True}


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    action = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    time = models.TimeField()
    is_pleasant = models.BooleanField(default=False)
    linked_habit = models.ForeignKey("self", on_delete=models.SET_NULL, **NULLABLE)
    period = models.PositiveIntegerField(
        default=1
    )  # Периодичность выполнения (по умолчанию ежедневно)
    reward = models.CharField(max_length=255, **NULLABLE)
    duration = models.PositiveIntegerField()  # Время на выполнение (в секундах)
    is_public = models.BooleanField(default=False)

    def clean(self):
        # Валидация: нельзя одновременно выбрать связанную привычку и вознаграждение
        if self.reward and self.linked_habit:
            raise ValidationError(
                "Нельзя указать одновременно вознаграждение и связанную привычку."
            )

        # Валидация: время на выполнение не должно превышать 120 секунд
        if self.duration > 120:
            raise ValidationError("Время выполнения не может превышать 120 секунд.")

        # Валидация: связанные привычки могут быть только с признаком приятных привычек
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной.")

        # Валидация: у приятной привычки не может быть вознаграждения или связанных привычек
        if self.is_pleasant and (self.reward or self.linked_habit):
            raise ValidationError(
                "Приятная привычка не может иметь вознаграждения или связанных привычек."
            )

        # Валидация: периодичность выполнения не может быть реже одного раза в неделю (7 дней)
        if self.period > 7:
            raise ValidationError(
                "Периодичность выполнения не может быть реже одного раза в неделю."
            )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"{self.action} в {self.time}"
