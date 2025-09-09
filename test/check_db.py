from app import app
from models.models import User, Task

with app.app_context():
    users = User.query.all()
    print("=== Users ===")
    for u in users:
        print(f"User: {u.username}, id={u.id}")

    tasks = Task.query.all()
    print("\n=== Tasks ===")
    for t in tasks:
        print(
            f"ID={t.id} | Title={t.title} | Status={t.status} | "
            f"Type={t.type} | Priority={t.priority} | Start={t.start_date} | "
            f"Deadline={t.deadline} | Tags={t.tags} | TaskType={t.task_type} | "
            f"StatusDate={t.status_date} | UserID={t.user_id}"
        )


# from app import app
# from models.models import db
#
# with app.app_context():
#     db.drop_all()
#     db.create_all()
#     print("DB recreated!")
