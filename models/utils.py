from datetime import date, datetime, timedelta
from flask import render_template, redirect, url_for
import models.services as svc


def parse_custom_date(date_str):
    """
    Parses a date in the format dd/mm/yyyy or yyyy-mm-dd

    Args:
        date_str: A string containing the date

    Returns:
        Date object or None
    """
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")


def format_tasks_for_display(tasks_objs, today):
    """
    Formats tasks for display on the frontend

    Args:
        tasks_objs: Dictionary of tasks by status
        today: Current date

    Returns:
        Formatted dictionary of tasks
    """
    tasks = {}
    for col in ["todo", "in_progress", "waiting", "done"]:
        tasks[col] = []
        for t in tasks_objs.get(col, []):
            status_date = t.status_date or today
            tasks[col].append({
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "type": t.type,
                "priority": t.priority,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "deadline": t.deadline.isoformat() if t.deadline else None,
                "tags": t.tags,
                "task_type": t.task_type,
                "status_date": status_date,
                "days_in_status": (today - status_date).days,
                "comment": t.comment,
                "username": t.user.username
            })
    return tasks


def handle_users_view(selected_user, users, view):
    """
    Handles the standard users view

    Args:
        selected_user: Selected user
        users: List of all users
        view: Current view

    Returns:
        Rendered template
    """
    if not users:
        return render_template("index.html", tasks={}, selected_user=None, users=[],
                               today=date.today().isoformat(), no_users=True, view=view)

    if not selected_user or selected_user == "all":
        selected_user = users[0] if users else None
    elif selected_user == "all":
        return redirect(url_for("index", user=users[0] if users else None, view=view))

    tasks_objs = svc.get_tasks_from_db(selected_user)
    today = date.today()

    tasks = format_tasks_for_display(tasks_objs, today)

    return render_template(
        "index.html",
        tasks=tasks,
        selected_user=selected_user,
        users=users,
        today=today.isoformat(),
        view=view
    )


def handle_vacation_view(selected_user, users, view):
    """
    Handles the vacation view

    Args:
        selected_user: Selected user
        users: List of all users
        view: Current view

    Returns:
        Rendered template
    """
    if not users:
        return render_template(
            "index.html",
            tasks={},
            selected_user=None,
            users=[],
            today=date.today().isoformat(),
            no_users=True,
            view=view
        )

    today = date.today()

    if selected_user == "all":
        vacations_objs = svc.get_vacations("all")
    else:
        vacations_objs = svc.get_vacations(selected_user)

    tasks = {"todo": [], "in_progress": [], "waiting": [], "done": []}

    for v in vacations_objs:
        start_date_str = v.start_date.strftime("%d.%m.%Y")
        end_date_str = v.end_date.strftime("%d.%m.%Y")

        title = f"{v.user.username}"
        date_range = f"{start_date_str} - {end_date_str}"

        col = v.status if v.status in tasks else "todo"

        highlight = False
        if col == "todo" and (v.start_date <= today + timedelta(days=7)):
            highlight = True

        tasks[col].append({
            "id": v.id,
            "title": title,
            "date_range": date_range,
            "status": v.status,
            "start_date": v.start_date.isoformat(),
            "end_date": v.end_date.isoformat(),
            "comment": v.comment,
            "username": v.user.username,
            "is_vacation": True,
            "highlight": highlight
        })

    return render_template(
        "index.html",
        tasks=tasks,
        selected_user=selected_user or "all",
        users=users,
        today=today.isoformat(),
        view=view
    )


def handle_category_view(category, selected_user, users, view):
    """
    Handles the view for categories AD-HOC, REG, PRO

    Args:
        category: Task category
        selected_user: Selected user
        users: List of all users
        view: Current view

    Returns:
        Rendered template
    """
    if not selected_user or selected_user not in users:
        selected_user = "all"

    if selected_user == "all":
        tasks_objs = svc.get_tasks_by_category(category)
    else:
        tasks_objs = svc.get_tasks_by_category_and_user(category, selected_user)

    today = date.today()
    tasks = format_tasks_for_display(tasks_objs, today)

    return render_template(
        "index.html",
        tasks=tasks,
        selected_user=selected_user,
        users=users,
        today=today.isoformat(),
        view=view
    )


def handle_backlog_view(users, view):
    """
    Handles the backlog view - all tasks for all users

    Args:
        users: List of all users
        view: Current view

    Returns:
        Rendered template
    """
    tasks_objs = svc.get_all_tasks()
    today = date.today()

    tasks = format_tasks_for_display(tasks_objs, today)

    return render_template(
        "index.html",
        tasks=tasks,
        selected_user="all",
        users=users,
        today=today.isoformat(),
        view=view
    )