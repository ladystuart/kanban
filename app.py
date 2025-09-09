import os
from datetime import date
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from dotenv import load_dotenv
from models.models import init_db
import models.services as svc
from models.utils import (
    parse_custom_date,
    handle_users_view,
    handle_vacation_view,
    handle_category_view,
    handle_backlog_view
)

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

    view = request.form.get("view", "users")
    return redirect(url_for("index", user=username, view=view))


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

    view = request.args.get("view", "users")
    return redirect(url_for("index", user=selected_user, view=view))


@app.route("/")
def index():
    """
    Display the main planner page with different views.

    - Redirects to login page if the user is not logged in.
    - Retrieves view type and selected user from query parameters.
    - Loads tasks based on the selected view.
    - Passes tasks, users, and other context variables to the index template.

    Returns:
        Response: Rendered HTML template for the planner's main page,
        or a redirect to the login page if not logged in.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    view = request.args.get("view", "users")
    selected_user = request.args.get("user")

    users = [u.username for u in svc.User.query.all()]

    if view == "users":
        return handle_users_view(selected_user, users, view)
    elif view in ["ad-hoc", "reg", "pro"]:
        return handle_category_view(view.upper(), selected_user, users, view)
    elif view == "vacation":
        return handle_vacation_view(selected_user, users, view)
    elif view == "backlog":
        return handle_backlog_view(users, view)
    else:
        return handle_users_view(selected_user, users, "users")


@app.route("/get_vacations_data")
def get_vacations_data():
    """
    Return vacations data in JSON format for Gantt chart

    Returns:
        JSON response with vacations data
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    vacations = svc.get_gantt_vacations()

    vacations_data = []
    for vacation in vacations:
        vacations_data.append({
            "id": vacation.id,
            "username": vacation.user.username,
            "start_date": vacation.start_date.isoformat(),
            "end_date": vacation.end_date.isoformat(),
            "status": vacation.status,
            "comment": vacation.comment
        })

    return jsonify(vacations_data)


@app.route("/delete_vacation", methods=["POST"])
def delete_vacation():
    """
    Delete vacation from database

    Returns:
        Redirect to index page
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    vacation_id = int(request.form.get("vacation_id"))
    user = request.form.get("user")
    view = request.form.get("view", "vacation")

    svc.delete_vacation(vacation_id)
    return redirect(url_for("index", user=user, view=view))


@app.route("/add_vacation", methods=["POST"])
def add_vacation_route():
    """
    Add new vacation

    Returns:
        Redirect to index page
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_name = request.form.get("user")
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")
    comment = request.form.get("comment", "")
    status = request.form.get("status", "todo")

    if not start_date_str or not end_date_str:
        flash("Please enter both start and end dates for vacation.", "error")
        return redirect(url_for("index", user=user_name, view="vacation"))

    start_date = parse_custom_date(start_date_str)
    end_date = parse_custom_date(end_date_str)

    svc.add_vacation(user_name, start_date, end_date, comment, status)
    return redirect(url_for("index", user=user_name, view="vacation"))


@app.route("/delete_vacation/<int:vacation_id>")
def delete_vacation_route(vacation_id):
    """
    Delete vacation by ID

    Args:
        vacation_id: ID отпуска

    Returns:
        Redirect to index page
    """
    svc.delete_vacation(vacation_id)
    return redirect(url_for("index", view="vacation"))


@app.route("/add", methods=["POST"])
def add_task():
    """
    Add a new task for the selected user.

    Returns:
        Response: Redirect to the index page with the selected user and view,
        or redirect to the login/index page if not logged in
        or no valid user was provided.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    selected_user = request.form.get("user")
    title = request.form.get("task_title")
    view = request.form.get("view", "users")

    if not selected_user or selected_user == "all" or not svc.User.query.filter_by(username=selected_user).first():
        flash("Please select a specific user to add tasks.", "error")
        if view == "users":
            users = [u.username for u in svc.User.query.all()]
            if users:
                return redirect(url_for("index", user=users[0], view=view))
        return redirect(url_for("index", view=view))

    status = request.form.get("status", "todo")
    task_type = request.form.get("type", "task")
    priority = request.form.get("priority", "medium")
    start_date_str = request.form.get("start_date") or date.today().isoformat()
    deadline_str = request.form.get("deadline") or None
    tags = [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()]
    task_category = request.form.get("task_type", "REG")
    comment = request.form.get("comment", "")

    start_date = parse_custom_date(start_date_str)
    deadline = parse_custom_date(deadline_str) if deadline_str else None

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

    return redirect(url_for("index", user=selected_user, view=view))


@app.route("/edit_vacation", methods=["POST"])
def edit_vacation():
    """
    Edit existing vacation

    Returns:
        Redirect to index page
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    vacation_id = int(request.form.get("vacation_id"))
    status = request.form.get("status")
    start_date = parse_custom_date(request.form.get("start_date"))
    end_date = parse_custom_date(request.form.get("end_date"))
    comment = request.form.get("comment", "")

    user = request.form.get("user", "all")

    svc.edit_vacation(vacation_id, status, start_date, end_date, comment)

    return redirect(url_for("index", user=user, view="vacation"))


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
    view = request.form.get("view", "users")
    start_date_str = request.form.get("start_date")
    deadline_str = request.form.get("deadline") or None

    start_date = parse_custom_date(start_date_str)
    deadline = parse_custom_date(deadline_str) if deadline_str else None

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

    return redirect(url_for("index", user=user, view=view))


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
    view = request.form.get("view", "users")
    svc.delete_task_from_db(task_id)
    return redirect(url_for("index", user=user, view=view))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)