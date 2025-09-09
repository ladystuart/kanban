from datetime import date
from models.models import db, User, Task


def add_user_to_db(username):
    """
    Add a new user to the database if they do not already exist.

    :param username: The username of the user to add.
    :return: None
    """
    if not User.query.filter_by(username=username).first():
        user = User(username=username)
        db.session.add(user)
        db.session.commit()


def delete_user_from_db(username):
    """
    Delete a user from the database.

    :param username: The username of the user to delete.
    :return: None
    """
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()


def get_tasks_from_db(username):
    """
    Retrieve all tasks for a given user, organized by status.
    If the user does not exist, they will be created.

    :param username: The username of the user whose tasks to retrieve.
    :return: Dictionary of tasks grouped by status:
             {"todo": [], "in_progress": [], "waiting": [], "done": []}
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        add_user_to_db(username)
        user = User.query.filter_by(username=username).first()
    tasks = {"todo": [], "in_progress": [], "waiting": [], "done": []}
    for task in user.tasks:
        tasks[task.status].append(task)
    return tasks


def add_task_to_db(username, title, status, type_, priority, start_date, deadline, tags, task_type, comment):
    """
    Add a new task to the database for a specific user.

    :param username: The username of the task owner.
    :param title: The title of the task.
    :param status: The status of the task (todo, in_progress, waiting, done).
    :param type_: The type of the task (e.g., Task, ASAP).
    :param priority: Priority of the task (Blocker, Critical, Medium, Low, Minor).
    :param start_date: The start date of the task.
    :param deadline: The deadline for the task (optional).
    :param tags: List of tags associated with the task.
    :param task_type: The category of the task (AD-HOC, PRO, REG).
    :param comment: Additional comments for the task.
    :return: None
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        add_user_to_db(username)
        user = User.query.filter_by(username=username).first()

    task = Task(
        title=title,
        status=status,
        type=type_,
        priority=priority,
        start_date=start_date,
        deadline=deadline if deadline else None,
        tags=",".join(tags),
        task_type=task_type,
        user=user,
        status_date=date.today(),
        comment=comment
    )
    db.session.add(task)
    db.session.commit()


def edit_task_in_db(task_id, data):
    """
    Edit an existing task in the database.

    :param task_id: ID of the task to edit.
    :param data: Dictionary containing task fields to update.
    :return: None
    """
    task = Task.query.get(task_id)
    if task:
        task.title = data.get("title", task.title)
        task.status = data.get("status", task.status)
        task.type = data.get("type", task.type)
        task.priority = data.get("priority", task.priority)
        task.start_date = data.get("start_date", task.start_date)
        task.deadline = data.get("deadline") or task.deadline
        task.tags = ",".join(data.get("tags", task.tags.split(",")))
        task.task_type = data.get("task_type", task.task_type)
        task.comment = data.get("comment", task.comment)
        task.status_date = date.today()
        db.session.commit()


def delete_task_from_db(task_id):
    """
    Delete a task from the database.

    :param task_id: ID of the task to delete.
    :return: None
    """
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
