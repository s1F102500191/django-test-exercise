from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_HIGH, 'High'),
    ]
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

    def is_overdue_now(self):
        """
        テンプレートから引数なしで使える期限切れ判定。
        現在時刻と比較して期限が過ぎていれば True を返す。
        """
        if self.due_at is None:
            return False
        return self.due_at < timezone.now()
