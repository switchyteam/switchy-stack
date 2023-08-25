from flask import (
    Flask,
    request,
    flash,
    url_for,
    redirect,
    render_template,
    make_response,
    jsonify,
)
from view import view
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta


app = Flask(__name__, template_folder="src/templates", static_folder="src/static")
app.config.from_object("config.Config")
app.register_blueprint(view, url_prefix="/")

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column("task_id", db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    priority = db.Column(db.String(64))
    due_date = db.Column(db.Date())
    complete = db.Column(db.Boolean, default=False)  # Renamed from "done"

    def __init__(self, title, desc, priority, due_date, complete=False):
        self.title = title
        self.desc = desc
        self.priority = priority
        self.due_date = due_date
        self.complete = complete  # Renamed from "done"


@app.route("/")
def index():
    db.create_all()
    return render_template("index.html", tasks=Task.query.all())


@app.route("/create/", methods=["GET", "POST"])
def create():
    db.create_all()
    if request.method == "POST":
        if (
            not request.form["title"]
            or not request.form["desc"]
            or not request.form["priority"]
            or not request.form["due_date"]
        ):
            flash("Please enter all the fields", "error")
        else:
            task = Task(
                title=request.form["title"],
                desc=request.form["desc"],
                priority=request.form["priority"],
                due_date=request.form["due_date"],
            )

            db.session.add(task)
            db.session.commit()

            # flash('Record was successfully added')
            return redirect(url_for("index"))
    return render_template("create.html")


@app.route("/api/create", methods=["POST"])
def create_api():
    db.create_all()
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        required_fields = ["title", "description", "priority"]
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing fields"}), 400

        title = data["title"]
        description = data["description"]
        priority = data["priority"]

        # Calculate the due date as today plus 7 days
        due_date = datetime.now() + timedelta(days=7)
        due_date_str = due_date.strftime("%Y-%m-%d")  # Format as "YYYY-MM-DD"

        task = Task(
            title=title,
            desc=description,
            priority=priority,
            due_date=due_date_str
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({"message": "Task created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/<int:task_id>/edit/", methods=("GET", "POST"))
def edit(task_id):
    db.create_all()
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":

        if (
            not request.form["title"]
            or not request.form["desc"]
            or not request.form["priority"]
            or not request.form["due_date"]
        ):
            flash("Please enter all the fields", "error")
        else:
            title = request.form["title"]
            desc = request.form["desc"]
            priority = request.form["priority"]
            due_date = request.form["due_date"]

            task.title = title
            task.desc = desc
            task.priority = priority
            task.due_date = due_date
            task.complete = False
            db.session.add(task)
            db.session.commit()

            # flash('Record was successfully updated')
            return redirect(url_for("index"))

    return render_template("edit.html", task=task)


@app.post("/<int:task_id>/delete/")
def delete(task_id):
    db.create_all()
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

# @app.route("/<int:task_id>/complete/", methods=("POST",))
# def mark_complete(task_id):
#     db.create_all()
#     task = Task.query.get_or_404(task_id)
#     task.complete = not task.complete
#     db.session.add(task)
#     db.session.commit()
#     return redirect(url_for("index"))

@app.route("/<int:task_id>/complete/", methods=("POST",))
def mark_complete(task_id):
    db.create_all()
    task = Task.query.get_or_404(task_id)
    task.complete = not task.complete  # Toggle the complete status
    db.session.add(task)
    db.session.commit()
    return render_template("index.html", tasks=Task.query.all())
    
@app.route("/test_db")
def test_db():
    db.create_all()
    # db.session.commit()
    task = Task.query.first()
    if not task:
        u = Task(
            title="Charlie",
            desc="Dog",
            priority="NEW",
            due_date=datetime(2018, 3, 13)
        )
        db.session.add(u)
        db.session.commit()
    task = Task.query.first()
    return "Task '{}' is in the database".format(
        task.title, task.desc, task.priority, task.due_date
    )


@app.route("/unsplash/")
def unsplash():
    return render_template("unsplash.html")


# For debugging only
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
