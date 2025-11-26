from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    # include dependency IDs for input/output
    dependencies = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Task.objects.all(), required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
