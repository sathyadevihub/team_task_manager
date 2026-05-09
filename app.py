from flask import Flask, render_template, request, redirect, jsonify, session
import mysql.connector

app = Flask(__name__)

app.secret_key = "taskmanagersecret"


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="task_manager"
    )



@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "" or password == "":
            return "All fields required"

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cur.fetchone()

        conn.close()

        if user:

            session["user"] = user["username"]
            session["role"] = user["role"]

            return redirect("/dashboard")

        else:
            return "Invalid Username or Password"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if username == "" or password == "" or role == "":
            return "All fields required"

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
            (username, password, role)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")



@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()

    conn.close()

    total_projects = len(projects)
    total_tasks = len(tasks)

    completed_tasks = 0
    pending_tasks = 0

    for task in tasks:

        if task["status"] == "Completed":
            completed_tasks += 1
        else:
            pending_tasks += 1

    return render_template(
        "dashboard.html",
        projects=projects,
        tasks=tasks,
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        user=session["user"],
        role=session["role"]
    )



@app.route("/create_project", methods=["GET", "POST"])
def create_project():

    if request.method == "POST":

        name = request.form.get("name")

        if name == "":
            return "Project name required"

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO projects(name) VALUES(%s)",
            (name,)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create_project.html")



@app.route("/delete_project/<int:id>")
def delete_project(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM projects WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")



@app.route("/create_task", methods=["GET", "POST"])
def create_task():

    if request.method == "POST":

        title = request.form.get("title")
        assigned_to = request.form.get("assigned_to")
        status = request.form.get("status")

        if title == "" or assigned_to == "" or status == "":
            return "All fields required"

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO tasks(title,assigned_to,status)
            VALUES(%s,%s,%s)
            """,
            (title, assigned_to, status)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create_task.html")



@app.route("/delete_task/<int:id>")
def delete_task(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")



@app.route("/update_status/<int:id>")
def update_status(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tasks SET status='Completed' WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



@app.route("/api/projects")
def api_projects():

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM projects")

    data = cur.fetchall()

    conn.close()

    return jsonify(data)



@app.route("/api/tasks")
def api_tasks():

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM tasks")

    data = cur.fetchall()

    conn.close()

    return jsonify(data)



@app.route("/api/users")
def api_users():

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT id,username,role FROM users")

    data = cur.fetchall()

    conn.close()

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)