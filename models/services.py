from datetime import date
from models.models import db, User, Task, Vacation


def add_vacation(user_name, start_date, end_date, comment, status):
    """
    Add a vacation entry for a specific user.

    :param user_name: Username of the user.
    :param start_date: Vacation start date (datetime.date).
    :param end_date: Vacation end date (datetime.date).
    :param comment: Optional comment about the vacation.
    :param status: Vacation status (todo, in_progress, waiting, done).
    :return: None
    :raises ValueError: If the user is not found in the database.
    """
    user = User.query.filter_by(username=user_name).first()
    if not user:
        raise ValueError("User not found")

    vacation = Vacation(
        user_id=user.id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        comment=comment
    )
    db.session.add(vacation)
    db.session.commit()


def get_gantt_vacations():
    """
    Retrieve all vacations, ordered by username and start date.
    Useful for displaying a Gantt chart of vacations.

    :return: List of Vacation objects.
    """
    return Vacation.query.join(User).order_by(User.username, Vacation.start_date).all()


def get_vacations(user_name=None):
    """
    Retrieve vacations for a specific user or all users.

    :param user_name: Username to filter by, or "all"/None for all users.
    :return: List of Vacation objects for the user(s).
    """
    if user_name == "all" or not user_name:
        return Vacation.query.all()
    user = User.query.filter_by(username=user_name).first()
    return user.vacations if user else []


def delete_vacation(vacation_id):
    """
    Delete a vacation entry by its ID.

    :param vacation_id: ID of the vacation to delete.
    :return: None
    """
    vacation = Vacation.query.get(vacation_id)
    if vacation:
        db.session.delete(vacation)
        db.session.commit()


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


def edit_vacation(vacation_id, status, start_date, end_date, comment):
    """
    Edit an existing vacation in the database.

    :param vacation_id: ID of the vacation to edit
    :param status: New status (todo, in_progress, waiting, done)
    :param start_date: New start date
    :param end_date: New end date
    :param comment: New comment
    """
    try:
        vacation = Vacation.query.get(vacation_id)
        if vacation:
            vacation.status = status
            vacation.start_date = start_date
            vacation.end_date = end_date
            vacation.comment = comment
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error editing vacation: {e}")
        return False


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


def get_tasks_by_category(category):
    """
    Retrieve tasks by category, grouped by status.

    :param category: Task category (AD-HOC, PRO, REG, etc.).
    :return: Dictionary of tasks grouped by status.
    """
    tasks = Task.query.filter_by(task_type=category).all()
    return group_tasks_by_status(tasks)


def get_tasks_by_category_and_user(category, username):
    """
    Retrieve tasks for a specific user and category, grouped by status.

    :param category: Task category (AD-HOC, PRO, REG, etc.).
    :param username: Username of the task owner.
    :return: Dictionary of tasks grouped by status, or empty dict if user not found.
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        return {}

    tasks = Task.query.filter_by(user_id=user.id, task_type=category).all()
    return group_tasks_by_status(tasks)


def get_all_tasks():
    """
    Retrieve all tasks in the database, grouped by status.

    :return: Dictionary of tasks grouped by status.
    """
    tasks = Task.query.all()
    return group_tasks_by_status(tasks)


def group_tasks_by_status(tasks):
    """
    Group a list of Task objects by their status.

    :param tasks: List of Task objects.
    :return: Dictionary of tasks grouped by status:
             {"todo": [], "in_progress": [], "waiting": [], "done": []}
    """
    grouped = {
        "todo": [],
        "in_progress": [],
        "waiting": [],
        "done": []
    }

    for task in tasks:
        if task.status in grouped:
            grouped[task.status].append(task)

    return grouped
