function openSidebar(task, col, task_id) {
    const sidebar = document.getElementById('task-sidebar');
    sidebar.style.display = 'block';
    sidebar.style.right = '0';

    document.getElementById('sidebar-title').innerText = task.title;

    document.getElementById('sidebar-col').value = col;
    document.getElementById('sidebar-id').value = task_id;

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

function openSidebarFromLi(el, col) {
    const task = JSON.parse(el.getAttribute('data-task'));
    openSidebar(task, col, task.id);
}

function closeSidebar() {
    const sidebar = document.getElementById('task-sidebar');
    sidebar.style.right = '-400px';
    setTimeout(() => sidebar.style.display = 'none', 300);
}

document.getElementById('sidebar-form').addEventListener('submit', function() {
    const editableTitle = document.getElementById('sidebar-title').textContent;
    document.getElementById('sidebar-hidden-title').value = editableTitle;
});