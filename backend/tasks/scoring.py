# backend/tasks/scoring.py
from datetime import datetime, date
from typing import List, Dict, Tuple, Any, Set
from dateutil.parser import parse as parse_date  # dateutil is often available; if not, we'll fall back

# If dateutil isn't installed in your environment, install it with:
# pip install python-dateutil
# (or we will gracefully parse YYYY-MM-DD below)

def _parse_date_safe(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return parse_date(value).date()
    except Exception:
        # try YYYY-MM-DD naive parse
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

def detect_cycle(tasks: List[Dict[str, Any]]) -> Tuple[bool, List[List[int]]]:
    """
    Detect cycles in dependency graph.
    Input expects tasks to have unique 'id' fields (can be any hashable, but we convert to str).
    dependencies should be a list of ids referencing other tasks in the input set.
    Returns (has_cycle, list_of_cycles_as_lists_of_ids)
    """
    # Build adjacency
    id_map = {str(t.get('id', i)): t for i, t in enumerate(tasks)}
    adj = {tid: [] for tid in id_map.keys()}
    for tid, t in id_map.items():
        deps = t.get('dependencies') or []
        for d in deps:
            dstr = str(d)
            if dstr in adj:
                # edge tid -> dstr (task depends on dstr)
                adj[tid].append(dstr)

    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        if node in stack:
            # cycle found — record cycle path from first occurrence
            if node in path:
                idx = path.index(node)
                cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nbr in adj.get(node, []):
            dfs(nbr, path + [nbr])
        stack.remove(node)

    for n in adj:
        if n not in visited:
            dfs(n, [n])

    return (len(cycles) > 0, cycles)

def compute_priority_score(task: Dict[str, Any], tasks_by_id: Dict[str, Dict[str, Any]]=None, today: date = None) -> Tuple[float, str]:
    """
    Compute a score 0-100 for a single task and return (score, explanation).
    Components:
      - Urgency (0-40)
      - Importance (0-30)
      - Effort (0-15) -> lower estimated_hours gives higher contribution (quick wins)
      - Dependency impact (0-15) -> tasks that many others depend on get higher score
    """
    if today is None:
        today = date.today()

    # Read and validate fields (apply defaults)
    title = task.get('title', '<untitled>')
    importance = task.get('importance')
    try:
        importance = int(importance)
    except Exception:
        importance = 5
    importance = max(1, min(10, importance))

    est_hours = task.get('estimated_hours')
    try:
        est_hours = float(est_hours)
        if est_hours < 0:
            est_hours = 0.0
    except Exception:
        est_hours = 0.0

    due_date_raw = task.get('due_date')
    due_date = _parse_date_safe(due_date_raw)

    # URGENCY (0-40)
    urgency = 0.0
    urgency_note = ""
    if due_date is None:
        urgency = 5.0  # unknown due date -> small urgency
        urgency_note = "no due date"
    else:
        delta = (due_date - today).days
        if delta < 0:
            # past due -> highest urgency
            urgency = 40.0
            urgency_note = f"past due by {-delta} day(s)"
        else:
            # tasks within 30 days get higher urgency, outside 30 days low urgency
            window = 30
            urgency = max(0.0, (window - delta) / window) * 40.0
            urgency_note = f"due in {delta} day(s)"

    # IMPORTANCE (0-30)
    importance_score = (importance / 10.0) * 30.0

    # EFFORT (0-15) -> smaller hours = higher score
    # use inverse sigmoid-ish mapping: score = 15 * (1 / (1 + est_hours))
    effort_score = 15.0 * (1.0 / (1.0 + est_hours))
    effort_note = f"estimated {est_hours} hour(s)"

    # DEPENDENCY (0-15) -> number of tasks that depend on this task (dependents)
    dependents_count = 0
    dep_note = ""
    if tasks_by_id:
        # count tasks in tasks_by_id that list this task's id in dependencies
        tid = str(task.get('id'))
        for other in tasks_by_id.values():
            deps = other.get('dependencies') or []
            if any(str(d) == tid for d in deps):
                dependents_count += 1
        dep_note = f"{dependents_count} dependent(s)"
    # cap at 5 for scaling
    dependency_score = min(dependents_count, 5) / 5.0 * 15.0

    total = urgency + importance_score + effort_score + dependency_score
    # normalize to 0-100 (already approx 0-100)
    score = round(total, 2)

    # Build explanation
    explanation_parts = [
        f"urgency: {round(urgency,2)} ({urgency_note})",
        f"importance: {round(importance_score,2)} (rating {importance})",
        f"effort: {round(effort_score,2)} ({effort_note})",
        f"dependency: {round(dependency_score,2)} ({dep_note})"
    ]
    explanation = "; ".join(explanation_parts)

    return score, explanation

def analyze_tasks(tasks: List[Dict[str, Any]], today: date = None) -> Dict[str, Any]:
    """
    Main helper to analyze a list of tasks.
    Returns dict with:
      - tasks: list of task dicts enriched with 'score' and 'explanation'
      - cycles: list of cycles found (if any)
      - warnings: list of warnings about invalid inputs (if any)
    """
    if today is None:
        today = date.today()

    # Normalize ids to strings for internal mapping
    tasks_by_id = {}
    warnings = []
    for i, t in enumerate(tasks):
        tid = t.get('id', i)
        tasks_by_id[str(tid)] = t

    has_cycle, cycles = detect_cycle(tasks)
    if has_cycle:
        warnings.append("circular dependency detected")

    enriched = []
    for tid, t in tasks_by_id.items():
        # validate minimal fields
        if not t.get('title'):
            warnings.append(f"task {tid} missing title (set to '<untitled>')")
        score, explanation = compute_priority_score(t, tasks_by_id=tasks_by_id, today=today)
        out = dict(t)  # shallow copy
        out['score'] = score
        out['explanation'] = explanation
        enriched.append(out)

    # sort by score descending
    enriched_sorted = sorted(enriched, key=lambda x: x['score'], reverse=True)

    return {
        "tasks": enriched_sorted,
        "cycles": cycles,
        "warnings": warnings
    }
