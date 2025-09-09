import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, session, url_for, flash
from dotenv import load_dotenv
from models.models import init_db
import models.services as svc

load_dotenv()

PASSWORD = os.environ.get("APP_PASSWORD")
USERNAME = os.environ.get("APP_USERNAME")

app = Flask(__name__)
app.secret_key = "super_secret_key"

init_db(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login. On POST, verify credentials and start a session.
    On GET, render the login page.

    :return: Rendered login template or redirect to index if login successful.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Login or password incorrect")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Log out the current user by clearing the session.

    :return: Redirect to login page.
    """
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/add_user", methods=["POST"])
def add_user():
    """
    Add a new user to the database from the form submission.

    :return: Redirect to index page showing the newly added user.
    """
    username = request.form.get("username")
    if username:
        svc.add_user_to_db(username)
    return redirect(url_for("index", user=username))


@app.route("/delete_user/<username>")
def delete_user(username):
    """
    Delete a user from the database and select another user if available.

    :param username: The username of the user to delete.
    :return: Redirect to index page with a selected user.
    """
    svc.delete_user_from_db(username)
    remaining_users = [u.username for u in svc.User.query.all()]
    selected_user = remaining_users[0] if remaining_users else None
    return redirect(url_for("index", user=selected_user))


@app.route("/")
def index():
    """
    Display the main planner page.

    - Redirects to login page if the user is not logged in.
    - Retrieves all users and the currently selected user from query parameters.
    - Loads tasks from the database for the selected user and groups them by status.
    - Calculates days spent in the current status for each task.
    - Passes tasks, users, and other context variables to the index template.

    Returns:
        Response: Rendered HTML template for the planner's main page,
        or a redirect to the login page if not logged in.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    selected_user = request.args.get("user")
    users = [u.username for u in svc.User.query.all()]

    if not users:
        return render_template("index.html", tasks={}, selected_user=None, users=[],
                               today=date.today().isoformat(), no_users=True)

    if not selected_user:
        selected_user = users[0]

    tasks_objs = svc.get_tasks_from_db(selected_user)
    today = date.today()

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
                "comment": t.comment
            })

    return render_template(
        "index.html",
        tasks=tasks,
        selected_user=selected_user,
        users=users,
        today=today.isoformat()
    )


@app.route("/add", methods=["POST"])
def add_task():
    """
    Add a new task for the selected user.

    Returns:
        Response: Redirect to the index page with the selected user,
        or redirect to the login/index page if not logged in
        or no valid user was provided.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    selected_user = request.form.get("user")
    title = request.form.get("task_title")

    if not selected_user or not svc.User.query.filter_by(username=selected_user).first():
        flash("You didn't create a user. Please add one first.", "error")
        return redirect(url_for("index"))

    status = request.form.get("status", "todo")
    task_type = request.form.get("type", "задача")
    priority = request.form.get("priority", "средний")
    start_date_str = request.form.get("start_date") or date.today().isoformat()
    deadline_str = request.form.get("deadline") or None
    tags = [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()]
    task_category = request.form.get("task_type", "REG")
    comment = request.form.get("comment", "")

    start_date = datetime.fromisoformat(start_date_str).date()
    deadline = datetime.fromisoformat(deadline_str).date() if deadline_str else None

    if title:
        svc.add_task_to_db(
            selected_user,
            title,
            status,
            task_type,
            priority,
            start_date,
            deadline,
            tags,
            task_category,
            comment
        )

    return redirect(url_for("index", user=selected_user))


@app.route("/edit_task", methods=["POST"])
def edit_task():
    """
    Edit an existing task in the database based on the sidebar form submission.

    :return: Redirect to index page with updated task data.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user = request.form.get("user")
    task_id = int(request.form.get("task_id"))
    start_date_str = request.form.get("start_date")
    deadline_str = request.form.get("deadline") or None

    start_date = datetime.fromisoformat(start_date_str).date()
    deadline = datetime.fromisoformat(deadline_str).date() if deadline_str else None

    svc.edit_task_in_db(
        task_id=task_id,
        data={
            "title": request.form.get("title"),
            "status": request.form.get("status"),
            "type": request.form.get("type"),
            "priority": request.form.get("priority"),
            "start_date": start_date,
            "deadline": deadline,
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "task_type": request.form.get("task_type"),
            "comment": request.form.get("comment", "")
        }
    )

    return redirect(url_for("index", user=user))


@app.route("/delete_task", methods=["POST"])
def delete_task():
    """
    Delete a task from the database.

    :return: Redirect to index page with updated tasks.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    task_id = int(request.form.get("task_id"))
    user = request.form.get("user")
    svc.delete_task_from_db(task_id)
    return redirect(url_for("index", user=user))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
