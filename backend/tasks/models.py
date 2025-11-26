from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(default=0.0)
    importance = models.PositiveSmallIntegerField(default=5)  # 1-10
    # dependencies: tasks that this task depends on (i.e., blocks must be done first)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (importance={self.importance})"
