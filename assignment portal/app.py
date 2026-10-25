"""Assignment Submission Portal - Flask + SQLite backend.
Run:  pip install -r requirements.txt && python app.py
Cloud: deploy with `gunicorn app:app`; swap save_file()/file_path() for S3 (see README)."""
import os, sqlite3, uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
from flask import Flask, request, jsonify, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE = os.path.dirname(os.path.abspath(__file__))
SECRET = os.environ.get("SECRET_KEY", "change-me-in-production")
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "portal.db"))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BASE, "uploads"))
ALLOWED = {"pdf", "doc", "docx", "txt", "zip", "py", "ipynb", "ppt", "pptx"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('student','teacher')));
CREATE TABLE IF NOT EXISTS assignments(
  id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT,
  deadline TEXT NOT NULL, max_marks INTEGER DEFAULT 100,
  teacher_id INTEGER NOT NULL REFERENCES users(id));
CREATE TABLE IF NOT EXISTS submissions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  assignment_id INTEGER NOT NULL REFERENCES assignments(id),
  student_id INTEGER NOT NULL REFERENCES users(id),
  filename TEXT NOT NULL, stored_name TEXT NOT NULL, submitted_at TEXT NOT NULL,
  marks INTEGER, feedback TEXT, UNIQUE(assignment_id, student_id));
"""

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

with sqlite3.connect(DB_PATH) as c:
    c.executescript(SCHEMA)

def now(): return datetime.now(timezone.utc)

def make_token(u):
    return jwt.encode({"sub": str(u["id"]), "role": u["role"], "name": u["name"],
                       "exp": now() + timedelta(hours=12)}, SECRET, algorithm="HS256")

def auth(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            h = request.headers.get("Authorization", "")
            try:
                p = jwt.decode(h.removeprefix("Bearer "), SECRET, algorithms=["HS256"])
            except jwt.PyJWTError:
                return jsonify(error="Please sign in again."), 401
            if roles and p["role"] not in roles:
                return jsonify(error="You don't have access to this."), 403
            g.user = {"id": int(p["sub"]), "role": p["role"], "name": p["name"]}
            return fn(*a, **kw)
        return wrapper
    return deco

# ---- storage (swap these two for S3: boto3 upload_fileobj / generate_presigned_url)
def save_file(f):
    stored = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_DIR, stored))
    return stored

def delete_file(stored):
    try: os.remove(os.path.join(UPLOAD_DIR, stored))
    except FileNotFoundError: pass

# ---- auth routes
@app.post("/api/register")
def register():
    d = request.get_json(force=True)
    if not all(d.get(k) for k in ("name", "email", "password", "role")) or d["role"] not in ("student", "teacher"):
        return jsonify(error="Fill in name, email, password and role."), 400
    if len(d["password"]) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400
    try:
        cur = db().execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                           (d["name"].strip(), d["email"].lower().strip(),
                            generate_password_hash(d["password"]), d["role"]))
        db().commit()
    except sqlite3.IntegrityError:
        return jsonify(error="That email is already registered."), 409
    u = {"id": cur.lastrowid, "role": d["role"], "name": d["name"].strip()}
    return jsonify(token=make_token(u), role=u["role"], name=u["name"])

@app.post("/api/login")
def login():
    d = request.get_json(force=True)
    u = db().execute("SELECT * FROM users WHERE email=?", (d.get("email", "").lower().strip(),)).fetchone()
    if not u or not check_password_hash(u["password"], d.get("password", "")):
        return jsonify(error="Email or password is incorrect."), 401
    return jsonify(token=make_token(u), role=u["role"], name=u["name"])

# ---- assignments
@app.get("/api/assignments")
@auth()
def list_assignments():
    uid, role = g.user["id"], g.user["role"]
    if role == "teacher":
        rows = db().execute(
            """SELECT a.*, (SELECT COUNT(*) FROM submissions s WHERE s.assignment_id=a.id) AS submitted
               FROM assignments a WHERE teacher_id=? ORDER BY deadline""", (uid,)).fetchall()
    else:
        rows = db().execute(
            """SELECT a.*, u.name AS teacher, s.id AS submission_id, s.filename, s.submitted_at,
                      s.marks, s.feedback
               FROM assignments a JOIN users u ON u.id=a.teacher_id
               LEFT JOIN submissions s ON s.assignment_id=a.id AND s.student_id=?
               ORDER BY deadline""", (uid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/assignments")
@auth("teacher")
def create_assignment():
    d = request.get_json(force=True)
    if not d.get("title") or not d.get("deadline"):
        return jsonify(error="Title and deadline are required."), 400
    db().execute("INSERT INTO assignments(title,description,deadline,max_marks,teacher_id) VALUES(?,?,?,?,?)",
                 (d["title"].strip(), d.get("description", ""), d["deadline"],
                  int(d.get("max_marks") or 100), g.user["id"]))
    db().commit()
    return jsonify(ok=True), 201

@app.post("/api/assignments/<int:aid>/submit")
@auth("student")
def submit(aid):
    a = db().execute("SELECT * FROM assignments WHERE id=?", (aid,)).fetchone()
    if not a: return jsonify(error="Assignment not found."), 404
    if now() > datetime.fromisoformat(a["deadline"].replace("Z", "+00:00")):
        return jsonify(error="The deadline has passed."), 400
    f = request.files.get("file")
    if not f or not f.filename: return jsonify(error="Choose a file to upload."), 400
    if f.filename.rsplit(".", 1)[-1].lower() not in ALLOWED:
        return jsonify(error="Allowed types: " + ", ".join(sorted(ALLOWED))), 400
    old = db().execute("SELECT stored_name FROM submissions WHERE assignment_id=? AND student_id=?",
                       (aid, g.user["id"])).fetchone()
    if old: delete_file(old["stored_name"])
    stored = save_file(f)
    db().execute(
        """INSERT INTO submissions(assignment_id,student_id,filename,stored_name,submitted_at)
           VALUES(?,?,?,?,?)
           ON CONFLICT(assignment_id,student_id) DO UPDATE SET filename=excluded.filename,
           stored_name=excluded.stored_name, submitted_at=excluded.submitted_at, marks=NULL, feedback=NULL""",
        (aid, g.user["id"], secure_filename(f.filename), stored, now().isoformat()))
    db().commit()
    return jsonify(ok=True)

@app.get("/api/assignments/<int:aid>/submissions")
@auth("teacher")
def submissions(aid):
    a = db().execute("SELECT * FROM assignments WHERE id=? AND teacher_id=?", (aid, g.user["id"])).fetchone()
    if not a: return jsonify(error="Assignment not found."), 404
    rows = db().execute(
        """SELECT s.id, s.filename, s.submitted_at, s.marks, s.feedback, u.name, u.email
           FROM submissions s JOIN users u ON u.id=s.student_id
           WHERE s.assignment_id=? ORDER BY s.submitted_at""", (aid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/submissions/<int:sid>/grade")
@auth("teacher")
def grade(sid):
    d = request.get_json(force=True)
    s = db().execute("""SELECT s.id, a.max_marks FROM submissions s JOIN assignments a ON a.id=s.assignment_id
                        WHERE s.id=? AND a.teacher_id=?""", (sid, g.user["id"])).fetchone()
    if not s: return jsonify(error="Submission not found."), 404
    try: marks = int(d.get("marks"))
    except (TypeError, ValueError): return jsonify(error="Marks must be a number."), 400
    if not 0 <= marks <= s["max_marks"]:
        return jsonify(error=f"Marks must be between 0 and {s['max_marks']}."), 400
    db().execute("UPDATE submissions SET marks=?, feedback=? WHERE id=?", (marks, d.get("feedback", ""), sid))
    db().commit()
    return jsonify(ok=True)

@app.get("/api/submissions/<int:sid>/file")
@auth()
def download(sid):
    s = db().execute("""SELECT s.*, a.teacher_id FROM submissions s JOIN assignments a ON a.id=s.assignment_id
                        WHERE s.id=?""", (sid,)).fetchone()
    if not s or g.user["id"] not in (s["student_id"], s["teacher_id"]):
        return jsonify(error="File not found."), 404
    return send_from_directory(UPLOAD_DIR, s["stored_name"], as_attachment=True, download_name=s["filename"])

@app.get("/")
def index(): return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
