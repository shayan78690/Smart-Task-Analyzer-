from django.test import TestCase
from analyzer.scoring import calculate_priority_score

class PriorityScoreTests(TestCase):

    def test_high_urgency_scores_higher(self):
        task1 = {"due_date": "2025-11-30", "importance": 5, "estimated_hours": 3, "dependencies": []}
        task2 = {"due_date": "2025-12-30", "importance": 5, "estimated_hours": 3, "dependencies": []}

        score1 = calculate_priority_score(task1, dependents_count=0)
        score2 = calculate_priority_score(task2, dependents_count=0)

        self.assertTrue(score1 > score2)

    def test_low_effort_scores_higher(self):
        t1 = {"due_date": "2025-12-01", "importance": 5, "estimated_hours": 1, "dependencies": []}
        t2 = {"due_date": "2025-12-01", "importance": 5, "estimated_hours": 10, "dependencies": []}

        s1 = calculate_priority_score(t1, dependents_count=0)
        s2 = calculate_priority_score(t2, dependents_count=0)

        self.assertTrue(s1 > s2)

    def test_importance_impact(self):
        low = {"due_date": "2025-12-05", "importance": 2, "estimated_hours": 5, "dependencies": []}
        high = {"due_date": "2025-12-05", "importance": 9, "estimated_hours": 5, "dependencies": []}

        s_low = calculate_priority_score(low, dependents_count=0)
        s_high = calculate_priority_score(high, dependents_count=0)

        self.assertTrue(s_high > s_low)
