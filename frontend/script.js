// =========================
// STEP 1 — INITIAL SETUP
// =========================

// Store tasks added by user (in-memory)
let tasks = [];

// DOM elements
const form = document.getElementById("task-form");
const resultsDiv = document.getElementById("results");
const depSelect = document.getElementById("dependencies");
const warningBox = document.getElementById("warning-box");

// Helper: generate a unique ID for each task
function generateId() {
    return "task_" + Math.random().toString(36).substr(2, 9);
}

// Save tasks to localStorage
function saveTasksToStorage() {
    localStorage.setItem("tasks_data", JSON.stringify(tasks));
}

// Refresh dependency dropdown whenever tasks change
function updateDependencyDropdown() {
    depSelect.innerHTML = ""; // clear old

    tasks.forEach(task => {
        const option = document.createElement("option");
        option.value = task.id;
        option.textContent = `${task.title} (${task.id})`;
        depSelect.appendChild(option);
    });
}


// =========================
// STEP 13 — Load tasks on startup
// =========================

window.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("tasks_data");

    if (saved) {
        tasks = JSON.parse(saved);
        displayLocalTasks();
        updateDependencyDropdown();
    }
});


// =========================
// STEP 2 — HANDLE ADD TASK
// =========================

form.addEventListener("submit", function (e) {
    e.preventDefault();

    const title = document.getElementById("title").value.trim();
    const due_date = document.getElementById("due_date").value;
    const estimated_hours = parseFloat(document.getElementById("estimated_hours").value || "0");
    const importance = parseInt(document.getElementById("importance").value || "5");

    // Read dependencies from dropdown (multi-select)
    let dependencies = Array.from(depSelect.selectedOptions).map(opt => opt.value);

    // Basic validation
    if (!title) {
        alert("Task title is required.");
        return;
    }
    if (importance < 1 || importance > 10) {
        alert("Importance must be between 1 and 10.");
        return;
    }

    // Create task object
    const task = {
        id: generateId(),
        title,
        due_date,
        estimated_hours,
        importance,
        dependencies
    };

    // Add to list
    tasks.push(task);

    saveTasksToStorage();

    // Update dependency dropdown
    updateDependencyDropdown();

    // Show updated task list
    displayLocalTasks();

    // Reset form selection
    form.reset();
    depSelect.selectedIndex = -1;
});


// =========================
// STEP 3 — DISPLAY TASKS LOCALLY
// =========================

function displayLocalTasks() {
    resultsDiv.innerHTML = "";

    if (tasks.length === 0) {
        resultsDiv.innerHTML = "<p>No tasks added yet.</p>";
        return;
    }

    tasks.forEach(task => {
        const card = document.createElement("div");
        card.classList.add("task-card", "priority-low");

        card.innerHTML = `
            <h3>${task.title}</h3>
            <p><b>Due:</b> ${task.due_date || "N/A"}</p>
            <p><b>Hours:</b> ${task.estimated_hours}</p>
            <p><b>Importance:</b> ${task.importance}</p>
            <p><b>Dependencies:</b> ${task.dependencies.join(", ") || "None"}</p>
        `;

        resultsDiv.appendChild(card);
    });
}


// =========================
// STEP 4 — BULK JSON INPUT
// =========================

document.getElementById("load-bulk-btn").addEventListener("click", () => {
    const bulkText = document.getElementById("bulk-input").value.trim();

    if (!bulkText) {
        alert("Please paste a JSON array.");
        return;
    }

    try {
        const jsonTasks = JSON.parse(bulkText);

        if (!Array.isArray(jsonTasks)) {
            alert("JSON must be an array of tasks.");
            return;
        }

        // Append them to task list
        jsonTasks.forEach(t => {
            t.id = t.id || generateId();
            tasks.push(t);
        });

        saveTasksToStorage();

        updateDependencyDropdown();
        displayLocalTasks();

        alert("Bulk tasks loaded successfully!");
    } catch (err) {
        alert("Invalid JSON format.");
    }
});


// =========================
// STEP 5 — ANALYZE TASKS
// =========================

document.getElementById("analyze-btn").addEventListener("click", () => {
    if (tasks.length === 0) {
        alert("Please add tasks first.");
        return;
    }

    fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tasks)
    })
        .then(res => res.json())
        .then(data => {
            if (!data.tasks) {
                alert("Error analyzing tasks.");
                return;
            }

            // =========================
            // STEP 12 — Circular Dependency Warning
            // =========================
            if (data.cycles && data.cycles.length > 0) {
                warningBox.style.display = "block";
                warningBox.innerHTML = "<b>Warning:</b> Circular dependencies detected!<br>";

                data.cycles.forEach((cycle, index) => {
                    warningBox.innerHTML += `Cycle ${index + 1}: ${cycle.join(" → ")}<br>`;
                });
            } else {
                warningBox.style.display = "none";
            }

            // =========================
            // STEP 10 — Sorting strategy
            // =========================
            const strategy = document.getElementById("sort-strategy").value;
            let analyzed = data.tasks;

            if (strategy === "fastest") {
                analyzed = [...data.tasks].sort((a, b) => a.estimated_hours - b.estimated_hours);
            } 
            else if (strategy === "impact") {
                analyzed = [...data.tasks].sort((a, b) => b.importance - a.importance);
            } 
            else if (strategy === "deadline") {
                analyzed = [...data.tasks].sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
            }

            displayAnalyzedTasks(analyzed);
        })
        .catch(err => {
            alert("Failed to connect to backend.");
            console.error(err);
        });
});


// =========================
// STEP 6 — DISPLAY ANALYZED TASKS
// =========================

function displayAnalyzedTasks(analyzedTasks) {
    resultsDiv.innerHTML = "";

    analyzedTasks.forEach(task => {
        const card = document.createElement("div");

        if (task.score >= 70) {
            card.classList.add("task-card", "priority-high");
        } else if (task.score >= 50) {
            card.classList.add("task-card", "priority-medium");
        } else {
            card.classList.add("task-card", "priority-low");
        }

        card.innerHTML = `
            <div class="task-score">Score: ${task.score}</div>
            <h3>${task.title}</h3>
            <p><b>Due:</b> ${task.due_date || "N/A"}</p>
            <p><b>Hours:</b> ${task.estimated_hours}</p>
            <p><b>Importance:</b> ${task.importance}</p>
            <p><b>Dependencies:</b> ${task.dependencies.join(", ") || "None"}</p>
            <div class="task-explanation">${task.explanation}</div>
        `;

        resultsDiv.appendChild(card);
    });
}


// =========================
// STEP 7 — SUGGEST TOP 3
// =========================

document.getElementById("suggest-btn").addEventListener("click", () => {
    fetch("http://127.0.0.1:8000/api/tasks/suggest/")
        .then(res => res.json())
        .then(data => {
            if (!data.top_3) {
                alert("No suggestions received.");
                return;
            }
            displaySuggestedTasks(data.top_3);
        })
        .catch(err => {
            alert("Failed to connect to backend.");
            console.error(err);
        });
});


// =========================
// STEP 8 — DISPLAY SUGGESTED TASKS
// =========================

function displaySuggestedTasks(suggested) {
    resultsDiv.innerHTML = "<h3>Top 3 Suggestions</h3>";

    suggested.forEach(task => {
        const card = document.createElement("div");

        if (task.score >= 70) {
            card.classList.add("task-card", "priority-high");
        } else if (task.score >= 50) {
            card.classList.add("task-card", "priority-medium");
        } else {
            card.classList.add("task-card", "priority-low");
        }

        card.innerHTML = `
            <div class="task-score">Score: ${task.score}</div>
            <h3>${task.title}</h3>
            <p><b>Reason:</b> ${task.reason}</p>
            <p><b>Due:</b> ${task.due_date || "N/A"}</p>
            <p><b>Hours:</b> ${task.estimated_hours}</p>
            <p><b>Importance:</b> ${task.importance}</p>
            <div class="task-explanation">${task.explanation}</div>
        `;

        resultsDiv.appendChild(card);
    });
}
