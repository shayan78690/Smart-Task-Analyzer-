# backend/tasks/tests.py
from django.test import TestCase
from .scoring import compute_priority_score, analyze_tasks, detect_cycle
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import date, timedelta

class ScoringLogicTests(TestCase):
    def test_compute_priority_quick_vs_long(self):
        today = date.today()
        t_quick = {"id": "A", "title": "Quick", "due_date": (today + timedelta(days=5)).isoformat(), "estimated_hours": 0.5, "importance": 5}
        t_long = {"id": "B", "title": "Long", "due_date": (today + timedelta(days=5)).isoformat(), "estimated_hours": 20, "importance": 5}
        score_q, _ = compute_priority_score(t_quick, tasks_by_id={"A": t_quick, "B": t_long}, today=today)
        score_l, _ = compute_priority_score(t_long, tasks_by_id={"A": t_quick, "B": t_long}, today=today)
        self.assertGreater(score_q, score_l, "Quick task should score higher than very long task when importance and due date same")

    def test_detect_cycle(self):
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["3"]},
            {"id": "3", "dependencies": ["1"]},
        ]
        has_cycle, cycles = detect_cycle(tasks)
        self.assertTrue(has_cycle)
        self.assertTrue(len(cycles) >= 1)

class AnalyzeEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_api_analyze(self):
        url = '/api/tasks/analyze/'
        today = date.today()
        payload = [
            {"id": "t1", "title": "Fix bug", "due_date": (today + timedelta(days=2)).isoformat(), "estimated_hours": 2, "importance": 8, "dependencies": []},
            {"id": "t2", "title": "Write docs", "due_date": (today + timedelta(days=10)).isoformat(), "estimated_hours": 1, "importance": 6, "dependencies": ["t1"]},
        ]
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn('tasks', body)
        self.assertGreaterEqual(len(body['tasks']), 2)
        # top task should be one with higher computed score
        self.assertIn('score', body['tasks'][0])


class SuggestEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_api_suggest(self):
        url = '/api/tasks/suggest/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('top_3', data)
        self.assertEqual(len(data['top_3']), 3)
        self.assertIn('reason', data['top_3'][0])
