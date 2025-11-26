# 📌 Task Analyzer — Intelligent Task Prioritization System

**Task Analyzer** is an intelligent task-scoring and prioritization system built using **Django (Python)** for the backend and **HTML/CSS/JavaScript** for the frontend.

It analyzes tasks using a smart scoring algorithm, detects circular dependencies, suggests top-priority tasks, and provides multiple sorting strategies to customize the output.

This project was created as a part of the **Singularium Internship Assignment 2025**.

---

# 🚀 Features

### ✅ Smart Priority Score  
Each task is scored based on:
- **Urgency** (due date)
- **Importance**
- **Effort required**
- **Dependencies**
- **How many tasks depend on it**

### ✅ Circular Dependency Detection  
The system identifies task cycles, e.g.:


Task A → Task B → Task C → Task A


Displayed clearly in the frontend UI.

### ✅ Top 3 Task Suggestions  
Backend analyzes all tasks and suggests the top 3 tasks you should do **first**, with reasons.

### ✅ Sorting Strategies (Frontend)  
Choose how tasks are ordered:
- **Smart (Default)** → backend score  
- **Fastest** → lowest hours first  
- **Impact** → highest importance first  
- **Deadline** → nearest due date first  

### ✅ Bulk Task Import  
Paste a JSON array of tasks to load them instantly.

### ✅ LocalStorage Persistence  
Tasks remain saved even after refreshing the page.

### ✅ Beautiful & Intuitive UI  
Color-coded cards:
- 🔴 **High priority**  
- 🟡 **Medium priority**  
- 🟢 **Low priority**

---

# 🏗 Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Django (Python) |
| Frontend   | HTML, CSS, Vanilla JavaScript |
| Database   | SQLite (default) |
| Storage    | Browser LocalStorage |
| API Format | JSON REST API |

---

# 📂 Project Structure

task-analyzer/
│── backend/
│   ├── manage.py
│   ├── task_analyzer/
│   ├── analyzer/
│   │   ├── scoring.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│
│── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│
│── README.md



---

# ⚙️ Installation Instructions

## 1️⃣ Clone the Repository

git clone https://github.com/your-username/task-analyzer.git

cd task-analyzer

## 2️⃣ Setup Backend (Django)

cd backend
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Linux/Mac)

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Backend runs at:

http://127.0.0.1:8000/

## 3️⃣ Run Frontend

Simply open:
frontend/index.html

in your browser.  
No server required.

---

# 📡 API Documentation

## 🔹 1. Analyze Tasks  
**POST /api/tasks/analyze/**

**Input Example:**

```json
[
  {
    "id": "task_1",
    "title": "Fix login",
    "due_date": "2025-11-30",
    "estimated_hours": 3,
    "importance": 8,
    "dependencies": []
  }
]

Response Example:
{
  "tasks": [
    {
      "id": "task_1",
      "score": 85.3,
      "explanation": "urgency: 30.1; importance: 24; effort: 8; dependencies: 23"
    }
  ],
  "cycles": [],
  "warnings": []
}
🔹 2. Suggest Top 3 Tasks

GET /api/tasks/suggest/

Response Example:

{
  "top_3": [
    {
      "id": "task_1",
      "reason": "Highest impact and earliest due date",
      "score": 92.1
    }
  ]
}


🧮 Scoring Algorithm (Backend Logic)

A task's score is computed from 4 factors:

Factor	Weight	Description
Urgency	40%	Near due date → higher score
Importance	30%	User-defined importance (1–10)
Effort	20%	Less hours → higher score
Dependency Influence	10%	Tasks with many dependents get higher priority

Example:

urgency: 34.67 (due in 2 days)
importance: 24 (rating 8)
effort: 3.75 (3 hours)
dependency: 3 (1 dependent)

🎨 UI Highlights

Dynamic task cards

Color-coded priority visualization

Smart warnings for circular dependencies

Dropdown multi-select for dependencies

LocalStorage persistence




🧪 How to Test

Add tasks manually

Load bulk tasks

Analyze tasks

Try different sorting strategies

Get top 3 suggestions

Test circular dependencies

Refresh page → tasks should remain saved

🏁 Future Enhancements

Dependency graph visualization

Export tasks to CSV/PDF

AI-based task description analysis

Team-level workspaces

Eisenhower Matrix View

🧑‍💻 Author

Mo Shayan Ul Haque
Internship Assignment — Singularium Technologies
Task Analyzer Project (2025)



1. I chose a weighted scoring algorithm (Urgency 40%, Importance 30%, Effort 20%, Dependency Influence 10%) 
   because it balances practical engineering trade-offs mentioned in the assignment.

2. Circular dependency detection was implemented using DFS because it is optimal for directed graphs.

3. Sorting strategies were implemented on the frontend to demonstrate critical thinking and provide 
   user-controlled behavior.

4. LocalStorage was added to improve user experience even though it was not required, 
   ensuring data persistence without a database.

5. The UI was intentionally kept simple and human-designed instead of over-styled to match assignment goals.
