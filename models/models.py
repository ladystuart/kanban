import os
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key.
        username (str): Unique username of the user.
        tasks (list[Task]): List of tasks associated with the user.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")


class Task(db.Model):
    """
    Represents a task in the system.

    Attributes:
        id (int): Primary key.
        title (str): Title of the task.
        status (str): Status of the task (e.g., todo, in_progress, waiting, done).
        type (str): Type of task (default: "задача").
        priority (str): Priority of the task (default: "средний").
        start_date (date): Date when the task starts (default: today).
        deadline (date): Optional deadline date for the task.
        tags (str): Comma-separated tags for the task.
        task_type (str): Task category (default: "REG").
        status_date (date): Date when the status was last updated (default: today).
        user_id (int): Foreign key referencing the user.
        comment (str): Optional comment for the task.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default="todo")
    type = db.Column(db.String(20), default="задача")
    priority = db.Column(db.String(20), default="средний")
    start_date = db.Column(db.Date, default=date.today)
    deadline = db.Column(db.Date, nullable=True)
    tags = db.Column(db.String, default="")
    task_type = db.Column(db.String(20), default="REG")
    status_date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, default="")


def init_db(app: Flask):
    """
    Initialize the database with the given Flask app.

    Sets up the SQLAlchemy database URI from environment variables or defaults to a local SQLite database.
    Creates all tables defined in the models.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        None
    """
    DB_URL = os.environ.get("DATABASE_URL") or "sqlite:///local.db"
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
