// Flatpickr initialization
document.addEventListener('DOMContentLoaded', function() {
    // Date fields for tasks
    flatpickr("input[name='start_date']", {
        dateFormat: "d/m/Y",
        defaultDate: "today"
    });

    flatpickr("input[name='deadline']", {
        dateFormat: "d/m/Y"
    });

    // Date fields for vacations
    flatpickr("#add_vacation input[name='start_date']", {
        dateFormat: "d/m/Y"
    });

    flatpickr("#add_vacation input[name='end_date']", {
        dateFormat: "d/m/Y"
    });

    // Sidebar editing fields
    flatpickr("#sidebar-start-date", { dateFormat: "d/m/Y" });
    flatpickr("#sidebar-deadline", { dateFormat: "d/m/Y" });
    flatpickr("#vacation-start-date", { dateFormat: "d/m/Y" });
    flatpickr("#vacation-end-date", { dateFormat: "d/m/Y" });

    // Gantt chart date fields
    flatpickr("#gantt-start-date", {
        dateFormat: "d/m/Y",
    });

    flatpickr("#gantt-end-date", {
        dateFormat: "d/m/Y",
    });

    // Initialize UI
    window.addEventListener("load", () => {
        document.body.classList.add("loaded");
    });
});

/**
 * Opens the task sidebar and populates it with task data
 * @param {Object} task - The task object containing task data
 * @param {string} col - The column where the task is located
 * @param {number} task_id - The unique identifier of the task
 * @param {string} view - The current view mode
 */
function openSidebar(task, col, task_id, view) {
    const sidebar = document.getElementById('task-sidebar');
    sidebar.style.display = 'block';
    sidebar.style.right = '0';

    document.getElementById('sidebar-title').innerText = task.title;

    document.getElementById('sidebar-col').value = col;
    document.getElementById('sidebar-id').value = task_id;

    const viewInput = document.getElementById('sidebar-view');
    if (viewInput) {
        viewInput.value = view;
    } else {
        const newViewInput = document.createElement('input');
        newViewInput.type = 'hidden';
        newViewInput.name = 'view';
        newViewInput.id = 'sidebar-view';
        newViewInput.value = view;
        document.getElementById('sidebar-form').appendChild(newViewInput);
    }

    document.getElementById('sidebar-status').value = task.status;
    document.getElementById('sidebar-type').value = task.type;
    document.getElementById('sidebar-priority').value = task.priority;
    document.getElementById('sidebar-start-date').value = task.start_date;
    document.getElementById('sidebar-deadline').value = task.deadline !== "-" ? task.deadline : "";
    document.getElementById('sidebar-tags').value = task.tags;
    document.getElementById('sidebar-task-type').value = task.task_type;
    document.getElementById('delete-task-id').value = task.id;
    document.getElementById('sidebar-comment').value = task.comment || "";
}

/**
 * Opens sidebar from list item click event
 * @param {HTMLElement} el - The clicked list item element
 * @param {string} col - The column where the task is located
 */
function openSidebarFromLi(el, col) {
    const task = JSON.parse(el.getAttribute('data-task'));
    const urlParams = new URLSearchParams(window.location.search);
    const view = urlParams.get('view') || 'users';
    openSidebar(task, col, task.id, view);
}

/**
 * Closes the task sidebar with animation
 */
function closeSidebar() {
    const sidebar = document.getElementById('task-sidebar');
    sidebar.style.right = '-400px';
    setTimeout(() => sidebar.style.display = 'none', 300);
}

// Add event listener for sidebar form submission
document.getElementById('sidebar-form').addEventListener('submit', function() {
    const editableTitle = document.getElementById('sidebar-title').textContent;
    document.getElementById('sidebar-hidden-title').value = editableTitle;

    const urlParams = new URLSearchParams(window.location.search);
    const view = urlParams.get('view') || 'users';
    const viewInput = document.getElementById('sidebar-view');
    if (viewInput) {
        viewInput.value = view;
    }
});

// Add event listener for task deletion form submission
document.getElementById('delete-task-form').addEventListener('submit', function(e) {
    const urlParams = new URLSearchParams(window.location.search);
    const view = urlParams.get('view') || 'users';
    const viewInput = this.querySelector('input[name="view"]');
    if (viewInput) {
        viewInput.value = view;
    } else {
        const newViewInput = document.createElement('input');
        newViewInput.type = 'hidden';
        newViewInput.name = 'view';
        newViewInput.value = view;
        this.appendChild(newViewInput);
    }
});

/**
 * Updates the UI based on the current view mode
 */
function updateUIForView() {
    const urlParams = new URLSearchParams(window.location.search);
    const view = urlParams.get('view') || 'users';
    const userSelect = document.getElementById('user');
    const addTaskForm = document.getElementById('add-task-form');
    const userManagementForms = document.querySelectorAll('form[action="/add_user"], form[action^="/delete_user/"]');

    if (addTaskForm) {
        addTaskForm.style.display = 'none';
    }

    if (userSelect) {
        const allOption = userSelect.querySelector('option[value="all"]');

        if (view === 'users' && allOption) {
            allOption.style.display = 'none';

            if (userSelect.value === 'all' && userSelect.options.length > 1) {
                userSelect.value = userSelect.options[1].value;
            }
        } else if (allOption) {
            allOption.style.display = 'block';
        }
    }

    if (view === 'users') {
        userManagementForms.forEach(form => {
            form.style.display = 'flex';
        });
    } else {
        userManagementForms.forEach(form => {
            form.style.display = 'none';
        });
    }

    if (addTaskForm) {
        const selectedUser = userSelect ? userSelect.value : '';
        if (selectedUser !== 'all' && view !== 'backlog') {
            addTaskForm.style.display = 'flex';
        }
    }

    if (view === 'backlog' && addTaskForm) {
        addTaskForm.style.display = 'none';
    }
}

// Initialize UI on document load
document.addEventListener('DOMContentLoaded', function() {
    updateUIForView();

    const viewSelect = document.getElementById('view');
    if (viewSelect) {
        viewSelect.addEventListener('change', function() {
            updateUIForView();
        });
    }
});

/**
 * Sets up drag and drop functionality for task columns
 */
function setupDragAndDrop() {
    const columns = document.querySelectorAll('.column');

    columns.forEach(column => {
        column.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '#e6f0ff';
        });

        column.addEventListener('dragleave', function() {
            this.style.backgroundColor = 'rgba(255,255,255,0.9)';
        });

        column.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.backgroundColor = 'rgba(255,255,255,0.9)';

            const taskId = e.dataTransfer.getData('text/plain');
            const newStatus = this.querySelector('h2').textContent.toLowerCase().replace(' ', '_');

            console.log(`Moving task ${taskId} to ${newStatus}`);
        });
    });
}

/**
 * Gets URL parameter value by name
 * @param {string} name - The parameter name to retrieve
 * @returns {string|null} The parameter value or null if not found
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Updates the days in status counter for all tasks
 */
function updateDaysInStatus() {
    const today = new Date().toISOString().split('T')[0];
    const taskItems = document.querySelectorAll('li[data-task]');

    taskItems.forEach(item => {
        const task = JSON.parse(item.getAttribute('data-task'));
        const statusDate = new Date(task.status_date);
        const todayDate = new Date(today);
        const diffTime = Math.abs(todayDate - statusDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        const daysElement = item.querySelector('small');
        if (daysElement) {
            daysElement.textContent = `Days in this status: ${diffDays}`;
        }

        task.days_in_status = diffDays;
        item.setAttribute('data-task', JSON.stringify(task));
    });
}

// Update days in status every 5 minutes
setInterval(updateDaysInStatus, 300000);

// Add keyboard shortcuts for sidebar
document.addEventListener('keydown', function(e) {
    const sidebar = document.getElementById('task-sidebar');
    if (sidebar.style.display === 'block') {
        if (e.key === 'Escape') {
            closeSidebar();
        }
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            document.getElementById('sidebar-form').dispatchEvent(new Event('submit'));
        }
    }
});

// Add change listeners for view and user select elements
const viewSelect = document.getElementById('view');
if (viewSelect) {
    viewSelect.addEventListener('change', function() {
        setTimeout(updateUIForView, 100);
    });
}

const userSelect = document.getElementById('user');
if (userSelect) {
    userSelect.addEventListener('change', function() {
        setTimeout(updateUIForView, 100);
    });
}

/**
 * Opens the vacation sidebar and populates it with vacation data
 * @param {Object} vacation - The vacation object containing vacation data
 * @param {string} col - The column where the vacation is located
 */
function openVacationSidebar(vacation, col) {
    const sidebar = document.getElementById('vacation-sidebar');
    sidebar.style.display = 'block';
    sidebar.style.right = '0';

    document.getElementById('vacation-sidebar-title').innerText = `${vacation.title} - Vacation`;
    document.getElementById('vacation-id').value = vacation.id;
    document.getElementById('vacation-status').value = vacation.status;
    document.getElementById('vacation-start-date').value = vacation.start_date;
    document.getElementById('vacation-end-date').value = vacation.end_date;
    document.getElementById('vacation-comment').value = vacation.comment || "";
    document.getElementById('delete-vacation-id').value = vacation.id;
}

/**
 * Opens vacation sidebar from list item click event
 * @param {HTMLElement} li - The clicked list item element
 * @param {string} col - The column where the vacation is located
 */
function openVacationSidebarFromLi(li, col) {
    const data = JSON.parse(li.dataset.vacation);
    document.getElementById("vacation-sidebar").style.display = "block";
    document.getElementById("vacation-sidebar-title").innerText = data.title;
    document.getElementById("vacation-id").value = data.id;
    document.getElementById("vacation-status").value = data.status;
    document.getElementById("vacation-start-date").value = data.start_date;
    document.getElementById("vacation-end-date").value = data.end_date;
    document.getElementById("vacation-comment").value = data.comment || "";

    document.getElementById("delete-vacation-id").value = data.id;
}

/**
 * Closes the vacation sidebar with animation
 */
function closeVacationSidebar() {
    const sidebar = document.getElementById('vacation-sidebar');
    sidebar.style.right = '-400px';
    setTimeout(() => sidebar.style.display = 'none', 300);
}

/**
 * Smoothly updates the UI with a delay
 */
function smoothUpdateUI() {
    setTimeout(updateUIForView, 50);
}

/**
 * Updates the tasks UI based on provided tasks data
 * @param {Object} tasks - The tasks data to display
 * @param {string} view - The current view mode
 */
function updateTasksUI(tasks, view) {
    const columns = document.querySelectorAll('.column');

    columns.forEach(column => {
        const colName = column.querySelector('h2').textContent.toLowerCase().replace(' ', '_');
        const ul = column.querySelector('ul');
        ul.innerHTML = '';

        if (tasks[colName]) {
            tasks[colName].forEach(task => {
                let li;
                if (view === 'vacation' && task.is_vacation) {
                    li = createVacationElement(task, colName);
                } else {
                    li = createTaskElement(task, colName);
                }
                ul.appendChild(li);
            });
        }
    });
}

/**
 * Creates a vacation element for display in the UI
 * @param {Object} vacation - The vacation object
 * @param {string} col - The column where the vacation should be displayed
 * @returns {HTMLElement} The created vacation list item element
 */
function createVacationElement(vacation, col) {
    const li = document.createElement('li');
    li.className = `${col} vacation-item`;
    li.setAttribute('data-vacation', JSON.stringify(vacation));
    li.onclick = () => openVacationSidebarFromLi(li, col);

    const content = document.createElement('div');

    const username = document.createElement('strong');
    username.textContent = vacation.title;

    const dateRange = document.createElement('small');
    dateRange.textContent = vacation.date_range;

    content.appendChild(username);
    content.appendChild(document.createElement('br'));
    content.appendChild(dateRange);

    if (vacation.comment) {
        const comment = document.createElement('small');
        comment.style.color = '#666';
        comment.textContent = vacation.comment;
        content.appendChild(document.createElement('br'));
        content.appendChild(comment);
    }

    li.appendChild(content);
    return li;
}

// Initialize event listeners on document load
document.addEventListener('DOMContentLoaded', function() {
    updateUIForView();

    const viewSelect = document.getElementById('view');
    const userSelect = document.getElementById('user');

    if (viewSelect) {
        viewSelect.addEventListener('change', smoothUpdateUI);
    }
    if (userSelect) {
        userSelect.addEventListener('change', smoothUpdateUI);
    }
});

// Global variables for Gantt chart
let ganttChart = null;
let vacationData = [];

/**
 * Opens the Gantt chart modal
 */
function openGanttModal() {
  document.getElementById('gantt-modal').style.display = 'block';
  loadVacationData();
}

/**
 * Closes the Gantt chart modal
 */
function closeGanttModal() {
  document.getElementById('gantt-modal').style.display = 'none';
  if (ganttChart) {
    ganttChart.destroy();
    ganttChart = null;
  }
}

/**
 * Loads vacation data for the Gantt chart via AJAX
 */
function loadVacationData() {
  fetch('/get_vacations_data')
    .then(response => response.json())
    .then(data => {
      vacationData = data;
      initGanttControls();
      renderGanttChart();
    })
    .catch(error => {
      console.error('Error loading vacation data:', error);
    });
}

/**
 * Initializes Gantt chart controls with default values
 */
function initGanttControls() {
  const today = new Date();
  const endOfYear = new Date(today.getFullYear(), 11, 31); 

  document.getElementById('gantt-start-date').value = formatDateForInput(today);
  document.getElementById('gantt-end-date').value = formatDateForInput(endOfYear);
}

/**
 * Formats a date for input field (YYYY-MM-DD format)
 * @param {Date} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDateForInput(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); 
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Updates the Gantt chart with current data and settings
 */
function updateGanttChart() {
  if (ganttChart) {
    ganttChart.destroy();
  }
  renderGanttChart();
}

/**
 * Groups vacations by username
 * @param {Array} vacations - Array of vacation objects
 * @returns {Object} Grouped vacations by username
 */
function groupVacationsByUser(vacations) {
  const grouped = {};
  vacations.forEach(vacation => {
    if (!grouped[vacation.username]) {
      grouped[vacation.username] = [];
    }
    grouped[vacation.username].push(vacation);
  });
  return grouped;
}

/**
 * Renders the Gantt chart with vacation data
 */
function renderGanttChart() {
    const startInput = document.getElementById("gantt-start-date").value;
    const endInput = document.getElementById("gantt-end-date").value;

    const parseDate = str => {
        const [d, m, y] = str.split('/');
        return new Date(`${y}-${m}-${d}`);
    }

    const startDate = parseDate(startInput);
    const endDate = parseDate(endInput);
    const today = new Date();

    const filteredData = vacationData.filter(vacation => {
        const vacationStart = new Date(vacation.start_date);
        const vacationEnd = new Date(vacation.end_date);
        return (vacationStart <= endDate && vacationEnd >= startDate);
    });

    const groupedData = groupVacationsByUser(filteredData);
    const users = Object.keys(groupedData);

    const datasets = [];

    users.forEach(username => {
        const userVacations = groupedData[username];

        userVacations.forEach(vacation => {
            const vacationStart = new Date(vacation.start_date);
            const vacationEnd = new Date(vacation.end_date);

            let color;
            if (vacation.status === 'done') {
                color = 'rgba(46, 204, 113, 0.9)'; 
            } else if (vacation.status === 'todo') {
                const daysUntilStart = Math.ceil((vacationStart - today) / (1000 * 60 * 60 * 24));
                if (daysUntilStart <= 7 && daysUntilStart >= 0) {
                    color = 'rgba(231, 76, 60, 0.9)'; 
                } else {
                    color = 'rgba(189, 195, 199, 0.9)';
                }
            } else if (vacation.status === 'in_progress') {
                color = 'rgba(52, 152, 219, 0.9)'; 
            } else if (vacation.status === 'waiting') {
                color = 'rgba(241, 196, 15, 0.9)';
            } else {
                color = 'rgba(149, 165, 166, 0.9)';
            }

            datasets.push({
                label: `${username} - ${vacation.status}`,
                data: [{
                    x: [vacation.start_date, vacation.end_date],
                    y: username
                }],
                backgroundColor: color,
                borderColor: getDarkerColor(color),
                borderWidth: 2,
                borderSkipped: false,
                borderRadius: 5,
                barPercentage: 0.7,
                categoryPercentage: 0.8
            });
        });
    });

    const ctx = document.getElementById('gantt-chart').getContext('2d');

    if (ganttChart) {
        ganttChart.destroy();
    }

    ganttChart = new Chart(ctx, {
        type: 'bar',
        data: {
            datasets: datasets
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'dd MMM yyyy'
                        }
                    },
                    min: startDate,
                    max: endDate,
                    title: {
                        display: true,
                        text: 'Period'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Users'
                    },
                    ticks: {
                        autoSkip: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            const datasetIndex = tooltipItems[0].datasetIndex;
                            const vacationInfo = datasets[datasetIndex].label.split(' - ');
                            return `${vacationInfo[0]} (${vacationInfo[1]})`;
                        },
                        label: function(context) {
                            const datasetIndex = context.datasetIndex;
                            const vacationInfo = datasets[datasetIndex].label.split(' - ');
                            const username = vacationInfo[0];
                            const status = vacationInfo[1];

                            const vacation = groupedData[username].find(v =>
                                v.status === status &&
                                v.start_date === context.raw.x[0] &&
                                v.end_date === context.raw.x[1]
                            );

                            if (vacation) {
                                const start = new Date(vacation.start_date).toLocaleDateString('en-GB');
                                const end = new Date(vacation.end_date).toLocaleDateString('en-GB');
                                const days = Math.ceil((new Date(vacation.end_date) - new Date(vacation.start_date)) / (1000 * 60 * 60 * 24)) + 1;
                                return [`${start} - ${end}`, `Days: ${days}`, `Comment: ${vacation.comment || 'none'}`];
                            }
                            return ['No data'];
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            maintainAspectRatio: false,
            responsive: true
        }
    });
}

/**
 * Gets color based on vacation status
 * @param {string} status - The vacation status
 * @returns {string} RGBA color string
 */
function getColorForStatus(status) {
  const colors = {
    'todo': 'rgba(189, 195, 199, 0.9)',       
    'in_progress': 'rgba(52, 152, 219, 0.9)',  
    'waiting': 'rgba(241, 196, 15, 0.9)',     
    'done': 'rgba(46, 204, 113, 0.9)'          
  };
  return colors[status] || 'rgba(149, 165, 166, 0.9)';
}

/**
 * Gets a darker version of the given color
 * @param {string} color - The original RGBA color string
 * @returns {string} Darker RGBA color string
 */
function getDarkerColor(color) {
    const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (match) {
        const r = Math.max(0, parseInt(match[1]) - 30);
        const g = Math.max(0, parseInt(match[2]) - 30);
        const b = Math.max(0, parseInt(match[3]) - 30);
        return color.replace(/rgba?\((\d+),\s*(\d+),\s*(\d+)/, `rgba(${r},${g},${b}`);
    }
    return color.replace('0.9', '1'); 
}

// Close modal when clicking outside of it
window.onclick = function(event) {
  const modal = document.getElementById('gantt-modal');
  if (event.target == modal) {
    closeGanttModal();
  }
};