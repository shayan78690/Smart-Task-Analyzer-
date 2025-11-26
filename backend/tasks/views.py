# backend/tasks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .scoring import analyze_tasks
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

class AnalyzeTasksView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        data = request.data
        if not isinstance(data, list):
            return Response({"detail": "Expected a JSON array of tasks."}, status=status.HTTP_400_BAD_REQUEST)
        # Each task should be a dict
        try:
            result = analyze_tasks(data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Error analyzing tasks", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuggestTasksView(APIView):
    """
    Suggest top 3 tasks based on sample input for now.
    Later, the frontend will pass actual tasks to this endpoint.
    """
    def get(self, request, format=None):
        sample_tasks = [
            {"id": "1", "title": "Fix login bug", "due_date": "2025-11-30", "estimated_hours": 3, "importance": 8, "dependencies": []},
            {"id": "2", "title": "Write unit tests", "due_date": "2025-11-28", "estimated_hours": 1, "importance": 7, "dependencies": ["1"]},
            {"id": "3", "title": "Prepare documentation", "due_date": "2025-12-05", "estimated_hours": 2, "importance": 6, "dependencies": []},
            {"id": "4", "title": "Optimize code", "due_date": "2025-11-27", "estimated_hours": 5, "importance": 9, "dependencies": []},
        ]

        result = analyze_tasks(sample_tasks)
        top_tasks = result["tasks"][:3]

        # Add reason field
        for t in top_tasks:
            t["reason"] = "Selected because it ranks among the highest-scoring tasks today."

        return Response({
            "top_3": top_tasks,
            "notes": "Demo version — will use frontend input in Step 5."
        }, status=status.HTTP_200_OK)
