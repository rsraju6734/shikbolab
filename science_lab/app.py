# -*- coding: utf-8 -*-
"""
ShikboLab SaaS - স্কুল/শিক্ষার্থীদের জন্য সাবস্ক্রিপশনভিত্তিক বাংলা বিজ্ঞান ল্যাব
চালানোর নিয়ম:  pip install flask  ->  python app.py  ->  http://localhost:5000
"""
import os, re, io, csv, time, secrets, sqlite3
from functools import wraps
from flask import (Flask, g, request, session, redirect, render_template, flash,
                   abort, send_from_directory, Response, jsonify, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape

# ====================================================================
#  ১. সেটিংস (এখানকার সংখ্যাগুলো নিজের মতো বদলাতে পারো)
# ====================================================================
BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.environ.get("CONTENT_DIR", os.path.join(BASE, "content"))   # science_lab ফোল্ডারের কপি
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "shikbolab.db"))
UPLOADS = os.path.join(BASE, "uploads")

SITE_NAME = "ShikboLab"
TRIAL_DAYS = 7                      # ডেমোর দিন (৭ বা ১৫ করতে পারো)
PAY_NUMBERS = {                     # <-- এখানে নিজের নাম্বার বসাও
    "bKash": "01XXXXXXXXX (Personal)",
    "Nagad": "01XXXXXXXXX (Personal)",
}
# লগইন ছাড়াই যে অধ্যায়গুলো সবাই দেখতে পারবে (ফ্রি প্রিভিউ)
FREE_CHAPTERS = {"chem-concepts-of-chemistry.html"}

# প্ল্যানের তালিকা (দাম ও লিমিট নমুনা, নিজের মতো ঠিক করো)
# students = শিক্ষার্থী সংখ্যা, teachers = শিক্ষক সংখ্যা, devices = একজন একসাথে কয়টি ডিভাইসে লগইন রাখতে পারবে
PLANS = [
    dict(id="trial", name="ফ্রি ডেমো", kind="both", students=30, teachers=2, devices=2, price_m=0, price_w=0,
         features=["সব অধ্যায় ও সব ল্যাব (ফুল এক্সেস)", "৩০ জন শিক্ষার্থী ও ২ জন শিক্ষক", "%d দিন বিনামূল্যে" % TRIAL_DAYS]),
    dict(id="solo", name="একক শিক্ষার্থী", kind="person", students=1, teachers=0, devices=2, price_m=99, price_w=35,
         features=["১ জন শিক্ষার্থী", "২টি ডিভাইসে লগইন", "সব অধ্যায়, ল্যাব, কুইজ", "নিজের অগ্রগতি দেখা"]),
    dict(id="family", name="পরিবার", kind="person", students=4, teachers=0, devices=2, price_m=249, price_w=89,
         features=["৪ জন পর্যন্ত শিক্ষার্থী", "প্রত্যেকের আলাদা লগইন", "সব অধ্যায়, ল্যাব, কুইজ", "সবার অগ্রগতি এক জায়গায়"]),
    dict(id="starter", name="স্কুল স্টার্টার", kind="school", students=100, teachers=5, devices=1, price_m=1500, price_w=550,
         features=["১০০ জন শিক্ষার্থী", "৫ জন শিক্ষক", "স্কুলের নাম ও লোগো", "শিক্ষকের অগ্রগতি প্যানেল", "এক্সেল/CSV দিয়ে একসাথে শিক্ষার্থী যোগ"]),
    dict(id="standard", name="স্কুল স্ট্যান্ডার্ড", kind="school", students=500, teachers=20, devices=1, price_m=4500, price_w=1600, popular=True,
         features=["৫০০ জন শিক্ষার্থী", "২০ জন শিক্ষক", "স্কুলের নাম ও লোগো", "শিক্ষকের অগ্রগতি প্যানেল", "অগ্রাধিকার সাপোর্ট"]),
    dict(id="pro", name="স্কুল প্রো", kind="school", students=1500, teachers=50, devices=1, price_m=9000, price_w=3200,
         features=["১৫০০ জন শিক্ষার্থী", "৫০ জন শিক্ষক", "স্কুলের নাম ও লোগো", "সব সুবিধা", "বিশেষ সাপোর্ট"]),
]
PLAN = {p["id"]: p for p in PLANS}
PERIODS = {"month": ("মাসিক", 30), "week": ("সাপ্তাহিক", 7)}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("HTTPS"))   # SSL লাগানোর পর HTTPS=1 দিও

def _secret():
    p = os.path.join(BASE, "secret.key")
    if not os.path.exists(p):
        with open(p, "w") as f: f.write(secrets.token_hex(32))
    return open(p).read().strip()
app.secret_key = os.environ.get("SECRET_KEY") or _secret()

# ====================================================================
#  ২. ডাটাবেস
# ====================================================================
SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, name TEXT NOT NULL, phone TEXT,
  logo TEXT, plan TEXT NOT NULL DEFAULT 'trial', status TEXT NOT NULL DEFAULT 'trial',
  expires_at INTEGER NOT NULL, created_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, role TEXT NOT NULL, name TEXT NOT NULL,
  username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, class_name TEXT, created_at INTEGER NOT NULL,
  FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS payments(
  id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER NOT NULL, plan TEXT NOT NULL, period TEXT NOT NULL,
  amount INTEGER NOT NULL, method TEXT, trx TEXT, sender TEXT, status TEXT NOT NULL DEFAULT 'pending',
  created_at INTEGER NOT NULL, decided_at INTEGER,
  FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS sessions(
  token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at INTEGER NOT NULL, last_seen INTEGER NOT NULL, ua TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS progress(
  user_id INTEGER NOT NULL, chapter TEXT NOT NULL, opens INTEGER NOT NULL DEFAULT 0, last_at INTEGER NOT NULL,
  best_score INTEGER, best_total INTEGER, PRIMARY KEY(user_id, chapter),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
"""

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def _close(_):
    d = g.pop("db", None)
    if d: d.close()

def q1(sql, *a): return db().execute(sql, a).fetchone()
def qa(sql, *a): return db().execute(sql, a).fetchall()
def ex(sql, *a):
    c = db().execute(sql, a); db().commit(); return c

def init_db():
    os.makedirs(UPLOADS, exist_ok=True)
    c = sqlite3.connect(DB_PATH); c.executescript(SCHEMA)
    if not c.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
        user = os.environ.get("ADMIN_USER", "admin")
        pw = os.environ.get("ADMIN_PASS") or secrets.token_urlsafe(9)
        c.execute("INSERT INTO users(account_id,role,name,username,password_hash,created_at) VALUES(NULL,'admin','মূল অ্যাডমিন',?,?,?)",
                  (user, generate_password_hash(pw), now()))
        c.commit()
        print("\n" + "=" * 60)
        print(" প্রথমবার চালু হলো! তোমার অ্যাডমিন লগইন (এটা লিখে রাখো):")
        print("   ইউজারনেম :", user)
        print("   পাসওয়ার্ড :", pw)
        print("   অ্যাডমিন পেজ: http://localhost:5000/admin")
        print("=" * 60 + "\n")
    c.close()

def now(): return int(time.time())

# ====================================================================
#  ৩. সাহায্যকারী ফাংশন ও টেমপ্লেট ফিল্টার
# ====================================================================
BD = "০১২৩৪৫৬৭৮৯"
@app.template_filter("bn")
def bn(v): return "".join(BD[int(c)] if c.isdigit() else c for c in str(v))
@app.template_filter("bdate")
def bdate(ts):
    if not ts: return "-"
    return bn(time.strftime("%d/%m/%Y", time.localtime(ts)))
@app.template_filter("bdt")
def bdt(ts):
    if not ts: return "-"
    return bn(time.strftime("%d/%m/%Y %H:%M", time.localtime(ts)))
@app.template_filter("taka")
def taka(v): return "৳" + bn(f"{int(v):,}")

def days_left(acc): return max(0, -(-(acc["expires_at"] - now()) // 86400))
def has_access(acc): return bool(acc) and acc["status"] != "suspended" and acc["expires_at"] > now()

def seat_counts(acc):
    students = q1("SELECT COUNT(*) c FROM users WHERE account_id=? AND role='student'", acc["id"])["c"]
    teachers = q1("SELECT COUNT(*) c FROM users WHERE account_id=? AND role='teacher'", acc["id"])["c"]
    if acc["kind"] == "person": students += 1       # একক/পরিবার অ্যাকাউন্টে মালিক নিজেও একজন শিক্ষার্থী
    return students, teachers

def csrf_token():
    if "csrf" not in session: session["csrf"] = secrets.token_hex(16)
    return session["csrf"]

def safe_next(n):
    return n if n and n.startswith("/") and not n.startswith("//") else None

_titles = None
def chapter_titles():
    global _titles
    if _titles is None:
        _titles = {}
        try:
            txt = open(os.path.join(CONTENT, "js", "chapters.js"), encoding="utf8").read()
            for m in re.finditer(r"title:'([^']*)'.*?file:'chapters/([^']+)'", txt):
                _titles[m.group(2)] = m.group(1)
        except OSError: pass
    return _titles

@app.context_processor
def inject():
    return dict(csrf_token=csrf_token, SITE_NAME=SITE_NAME, PLAN=PLAN, days_left=days_left, has_access=has_access, now=now())

# ====================================================================
#  ৪. লগইন সেশন (ডিভাইস লিমিটসহ)
# ====================================================================
@app.before_request
def load_user():
    g.user = g.account = None
    # CSRF সুরক্ষা
    if request.method == "POST":
        tok = request.form.get("_csrf") or request.headers.get("X-CSRF")
        if not tok or tok != session.get("csrf"):
            abort(400, "নিরাপত্তা টোকেন মেলেনি। পেজ রিফ্রেশ করে আবার চেষ্টা করো।")
    t = session.get("token")
    if t:
        row = q1("SELECT s.token, u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?", t)
        if row:
            g.user = row
            if row["account_id"]: g.account = q1("SELECT * FROM accounts WHERE id=?", row["account_id"])
            if now() - q1("SELECT last_seen l FROM sessions WHERE token=?", t)["l"] > 300:
                ex("UPDATE sessions SET last_seen=? WHERE token=?", now(), t)
        else:
            session.pop("token", None)
            if request.endpoint not in ("static",): flash("অন্য ডিভাইসে লগইন করায় এখান থেকে বের হয়ে গেছ।", "warn")

def start_session(user):
    token = secrets.token_urlsafe(24)
    ex("INSERT INTO sessions(token,user_id,created_at,last_seen,ua) VALUES(?,?,?,?,?)",
       token, user["id"], now(), now(), (request.headers.get("User-Agent") or "")[:200])
    limit = 5
    if user["account_id"]:
        acc = q1("SELECT * FROM accounts WHERE id=?", user["account_id"])
        limit = PLAN.get(acc["plan"], PLAN["trial"])["devices"]
    rows = qa("SELECT token FROM sessions WHERE user_id=? ORDER BY last_seen DESC", user["id"])
    for r in rows[limit:]:
        ex("DELETE FROM sessions WHERE token=?", r["token"])
    csrf = session.get("csrf")
    session.clear(); session["token"] = token
    if csrf: session["csrf"] = csrf

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not g.user: return redirect("/login?next=" + request.path)
        return f(*a, **k)
    return w

def roles(*rs):
    def deco(f):
        @wraps(f)
        @login_required
        def w(*a, **k):
            if g.user["role"] not in rs: abort(403)
            return f(*a, **k)
        return w
    return deco

_attempts = {}
def too_many(key):
    t = now(); lst = [x for x in _attempts.get(key, []) if t - x < 600]
    _attempts[key] = lst
    return len(lst) >= 6

# ====================================================================
#  ৫. পাবলিক পেজ: হোম, প্ল্যান, সাইনআপ, লগইন
# ====================================================================
def nav_html():
    if g.user and g.user["role"] == "admin":
        return '<a href="/admin" style="padding:8px 16px;border-radius:999px;background:#1f3a5f;color:#fff;font-weight:600">⚙️ অ্যাডমিন</a>'
    if g.user:
        label = escape(g.account["name"]) if g.account else escape(g.user["name"])
        extra = ""
        if g.account and g.account["status"] == "trial":
            extra = '<span style="font-size:13px;color:#b8600b;font-weight:700">ডেমো: %s দিন বাকি</span>' % bn(days_left(g.account))
        home = "/dashboard" if g.user["role"] == "owner" else ("/progress" if g.user["role"] == "teacher" else "/me")
        return ('%s<a href="%s" style="padding:8px 16px;border-radius:999px;background:#fff;border:2px solid #cfd9e1;color:#1f3a5f;font-weight:700;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">🏫 %s</a>'
                '<a href="/logout" style="padding:8px 14px;font-weight:600;color:#5b6b78">বের হও</a>') % (extra, home, label)
    return ('<a href="/plans" style="padding:8px 14px;font-weight:600;color:#1f3a5f">প্ল্যান</a>'
            '<a href="/login" style="padding:8px 14px;font-weight:600;color:#1f3a5f">লগইন</a>'
            '<a href="/signup" style="padding:9px 18px;border-radius:999px;background:linear-gradient(135deg,#1f3a5f,#2f5d9e);color:#fff;font-weight:700">ফ্রি ডেমো শুরু</a>')

@app.route("/")
@app.route("/index.html")
def home():
    p = os.path.join(CONTENT, "index.html")
    if not os.path.exists(p): abort(404, "content/index.html পাওয়া যায়নি। README দেখো।")
    html = open(p, encoding="utf8").read().replace("<!--USERNAV-->", nav_html())
    return Response(html, mimetype="text/html")

@app.route("/css/<path:f>")
def css(f): return send_from_directory(os.path.join(CONTENT, "css"), f)
@app.route("/js/<path:f>")
def js(f): return send_from_directory(os.path.join(CONTENT, "js"), f)

@app.route("/plans")
def plans():
    return render_template("plans.html", plans=PLANS, periods=PERIODS)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if g.user: return redirect("/")
    if request.method == "POST":
        f = request.form
        kind = f.get("kind") if f.get("kind") in ("school", "person") else "school"
        name, owner, phone = f.get("name", "").strip(), f.get("owner", "").strip(), f.get("phone", "").strip()
        user, pw = f.get("username", "").strip().lower(), f.get("password", "")
        err = None
        if len(name) < 2: err = "নাম লেখো (কমপক্ষে ২ অক্ষর)।"
        elif not re.fullmatch(r"[a-z0-9_.-]{4,30}", user): err = "ইউজারনেম ইংরেজিতে ৪–৩০ অক্ষরের হতে হবে (a-z, 0-9, _ . -)।"
        elif len(pw) < 6: err = "পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।"
        elif not re.fullmatch(r"01\d{9}", phone): err = "সঠিক মোবাইল নাম্বার দাও (যেমন 017XXXXXXXX)।"
        elif q1("SELECT 1 FROM users WHERE username=?", user): err = "এই ইউজারনেম আগেই নেওয়া হয়ে গেছে, অন্যটা চেষ্টা করো।"
        if err:
            flash(err, "err"); return render_template("signup.html", form=f), 400
        cur = ex("INSERT INTO accounts(kind,name,phone,plan,status,expires_at,created_at) VALUES(?,?,?,?,?,?,?)",
                 kind, name, phone, "trial", "trial", now() + TRIAL_DAYS * 86400, now())
        aid = cur.lastrowid
        cur = ex("INSERT INTO users(account_id,role,name,username,password_hash,created_at) VALUES(?,?,?,?,?,?)",
                 aid, "owner", owner or name, user, generate_password_hash(pw), now())
        start_session(q1("SELECT * FROM users WHERE id=?", cur.lastrowid))
        flash("স্বাগতম! তোমার %s দিনের ফ্রি ডেমো চালু হয়ে গেছে 🎉" % bn(TRIAL_DAYS), "ok")
        return redirect("/dashboard")
    return render_template("signup.html", form={"kind": request.args.get("kind", "school")})

@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user: return redirect("/")
    if request.method == "POST":
        user, pw = request.form.get("username", "").strip().lower(), request.form.get("password", "")
        key = (request.remote_addr, user)
        if too_many(key):
            flash("অনেকবার ভুল হয়েছে। ১০ মিনিট পর আবার চেষ্টা করো।", "err"); return render_template("login.html"), 429
        u = q1("SELECT * FROM users WHERE username=?", user)
        if not u or not check_password_hash(u["password_hash"], pw):
            _attempts.setdefault(key, []).append(now())
            flash("ইউজারনেম বা পাসওয়ার্ড ভুল।", "err"); return render_template("login.html"), 401
        start_session(u)
        nxt = safe_next(request.args.get("next"))
        if nxt: return redirect(nxt)
        return redirect({"admin": "/admin", "owner": "/dashboard", "teacher": "/progress"}.get(u["role"], "/me"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    if session.get("token"): ex("DELETE FROM sessions WHERE token=?", session["token"])
    session.pop("token", None); flash("বের হয়েছ। আবার এসো 👋", "ok")
    return redirect("/")

@app.route("/locked")
@login_required
def locked():
    return render_template("locked.html")

# ====================================================================
#  ৬. অধ্যায় দেখানো (লগইন ও মেয়াদ চেক করে) + অগ্রগতি ট্র্যাকিং
# ====================================================================
@app.route("/chapters/<name>")
def chapter(name):
    name = os.path.basename(name)
    path = os.path.join(CONTENT, "chapters", name)
    if not name.endswith(".html") or not os.path.isfile(path): abort(404)
    free = name in FREE_CHAPTERS
    if not free:
        if not g.user:
            flash("এই অধ্যায় দেখতে লগইন করো অথবা ফ্রি ডেমো শুরু করো।", "warn")
            return redirect("/login?next=" + request.path)
        if g.user["role"] != "admin" and not has_access(g.account):
            return redirect("/locked")
    html = open(path, encoding="utf8").read()
    bar = render_template("chapter_bar.html", free=free and not g.user)
    html = html.replace("<body>", "<body>" + bar, 1) if "<body>" in html else bar + html
    if g.user and g.user["role"] != "admin":
        tr = '<script>window.SL_CH=%r;window.SL_CSRF=%r;</script><script src="/static/track.js"></script>' % (name, csrf_token())
        i = html.rfind("</body>")
        html = html[:i] + tr + html[i:] if i >= 0 else html + tr
    return Response(html, mimetype="text/html")

@app.route("/api/track", methods=["POST"])
@login_required
def track():
    d = request.get_json(silent=True) or {}
    ch = os.path.basename(str(d.get("chapter", "")))
    if not ch.endswith(".html"): return jsonify(ok=False), 400
    uid, t = g.user["id"], now()
    if not q1("SELECT 1 FROM progress WHERE user_id=? AND chapter=?", uid, ch):
        ex("INSERT INTO progress(user_id,chapter,opens,last_at) VALUES(?,?,0,?)", uid, ch, t)
    if d.get("event") == "open":
        ex("UPDATE progress SET opens=opens+1,last_at=? WHERE user_id=? AND chapter=?", t, uid, ch)
    elif d.get("event") == "score":
        try: s, tot = int(d["score"]), int(d["total"])
        except (KeyError, ValueError, TypeError): return jsonify(ok=False), 400
        if 0 <= s <= tot <= 500:
            row = q1("SELECT best_score,best_total FROM progress WHERE user_id=? AND chapter=?", uid, ch)
            better = row["best_total"] is None or s * 1.0 / tot >= (row["best_score"] or 0) * 1.0 / max(1, row["best_total"])
            if better:
                ex("UPDATE progress SET best_score=?,best_total=?,last_at=? WHERE user_id=? AND chapter=?", s, tot, t, uid, ch)
    return jsonify(ok=True)

def progress_rows(acc_id, uid=None):
    sql = ("SELECT u.id uid,u.name,u.class_name,u.role,p.chapter,p.opens,p.best_score,p.best_total,p.last_at "
           "FROM users u LEFT JOIN progress p ON p.user_id=u.id WHERE u.account_id=? AND (u.role='student' OR (u.role='owner' AND (SELECT kind FROM accounts WHERE id=u.account_id)='person'))")
    args = [acc_id]
    if uid: sql += " AND u.id=?"; args.append(uid)
    out = {}
    for r in qa(sql + " ORDER BY u.class_name,u.name", *args):
        o = out.setdefault(r["uid"], dict(name=r["name"], cls=r["class_name"], role=r["role"], ch=[], last=0))
        if r["chapter"]:
            o["ch"].append(r); o["last"] = max(o["last"], r["last_at"] or 0)
    return out

@app.route("/me")
@roles("student", "owner", "teacher")
def me():
    data = progress_rows(g.account["id"], g.user["id"]).get(g.user["id"], dict(ch=[]))
    return render_template("me.html", data=data, titles=chapter_titles())

@app.route("/progress")
@roles("owner", "teacher")
def progress():
    return render_template("progress.html", students=progress_rows(g.account["id"]), titles=chapter_titles())

# ====================================================================
#  ৭. স্কুল / অ্যাকাউন্ট ড্যাশবোর্ড (মালিকের জন্য)
# ====================================================================
@app.route("/dashboard")
@roles("owner")
def dashboard():
    acc = g.account; s, t = seat_counts(acc); p = PLAN.get(acc["plan"], PLAN["trial"])
    pending = q1("SELECT COUNT(*) c FROM payments WHERE account_id=? AND status='pending'", acc["id"])["c"]
    return render_template("dash.html", s=s, t=t, p=p, pending=pending)

ROLE_BN = {"student": "শিক্ষার্থী", "teacher": "শিক্ষক"}

@app.route("/dashboard/people/<role>", methods=["GET", "POST"])
@roles("owner")
def people(role):
    if role not in ROLE_BN: abort(404)
    acc = g.account; p = PLAN.get(acc["plan"], PLAN["trial"])
    if role == "teacher" and acc["kind"] == "person": abort(404)
    limit = p["students"] if role == "student" else p["teachers"]
    creds = session.pop("creds", None)
    if request.method == "POST":
        act = request.form.get("act")
        if act == "delete":
            ex("DELETE FROM users WHERE id=? AND account_id=? AND role=?", request.form.get("id"), acc["id"], role)
            flash("মুছে ফেলা হয়েছে।", "ok")
        elif act == "reset":
            u = q1("SELECT * FROM users WHERE id=? AND account_id=? AND role=?", request.form.get("id"), acc["id"], role)
            if u:
                npw = str(secrets.randbelow(900000) + 100000)
                ex("UPDATE users SET password_hash=? WHERE id=?", generate_password_hash(npw), u["id"])
                ex("DELETE FROM sessions WHERE user_id=?", u["id"])
                session["creds"] = [(u["name"], u["username"], npw)]
        elif act in ("add", "bulk"):
            if not has_access(acc):
                flash("মেয়াদ শেষ। আগে প্ল্যান নাও।", "err"); return redirect(request.path)
            lines = []
            if act == "add":
                lines.append([request.form.get(k, "").strip() for k in ("name", "cls", "username", "password")])
            else:
                for ln in request.form.get("bulk", "").splitlines():
                    if ln.strip(): lines.append([c.strip() for c in next(csv.reader([ln]))])
            used = (seat_counts(acc)[0] if role == "student" else seat_counts(acc)[1])
            made, errs = [], []
            for row in lines:
                row += [""] * (4 - len(row))
                name, cls, user, pw = row[:4]
                if used + len(made) >= limit:
                    errs.append("লিমিট (%s জন) শেষ। বাকিগুলো যোগ হয়নি। প্ল্যান আপগ্রেড করো।" % bn(limit)); break
                if len(name) < 2: errs.append("নাম খালি: %r" % ",".join(row)); continue
                if not user:
                    user = "%s%d-%s" % ("s" if role == "student" else "t", acc["id"], secrets.token_hex(2))
                user = user.lower()
                if not re.fullmatch(r"[a-z0-9_.-]{4,30}", user): errs.append("ইউজারনেম ঠিক নয়: " + user); continue
                if q1("SELECT 1 FROM users WHERE username=?", user): errs.append("ইউজারনেম আগে থেকেই আছে: " + user); continue
                if not pw: pw = str(secrets.randbelow(900000) + 100000)
                elif len(pw) < 6: errs.append("পাসওয়ার্ড ছোট (কমপক্ষে ৬): " + name); continue
                ex("INSERT INTO users(account_id,role,name,username,password_hash,class_name,created_at) VALUES(?,?,?,?,?,?,?)",
                   acc["id"], role, name, user, generate_password_hash(pw), cls or None, now())
                made.append((name, user, pw))
            if made:
                session["creds"] = made; flash("%s জন যোগ হয়েছে।" % bn(len(made)), "ok")
            for e in errs: flash(e, "err")
        return redirect(request.path)
    people_rows = qa("SELECT * FROM users WHERE account_id=? AND role=? ORDER BY class_name,name", acc["id"], role)
    s, t = seat_counts(acc)
    return render_template("people.html", role=role, rb=ROLE_BN[role], rows=people_rows, limit=limit,
                           used=(s if role == "student" else t), creds=creds)

def read_image(fs):
    head = fs.read(16); fs.seek(0)
    if head.startswith(b"\x89PNG"): return "png"
    if head[:3] == b"\xff\xd8\xff": return "jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP": return "webp"
    return None

@app.route("/dashboard/brand", methods=["GET", "POST"])
@roles("owner")
def brand():
    acc = g.account
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if len(name) >= 2: ex("UPDATE accounts SET name=? WHERE id=?", name, acc["id"])
        f = request.files.get("logo")
        if f and f.filename:
            ext = read_image(f.stream)
            if not ext: flash("শুধু PNG, JPG বা WEBP ছবি দাও।", "err"); return redirect(request.path)
            os.makedirs(UPLOADS, exist_ok=True)
            fn = "logo%d.%s" % (acc["id"], ext)
            f.save(os.path.join(UPLOADS, fn)); ex("UPDATE accounts SET logo=? WHERE id=?", fn, acc["id"])
        if request.form.get("remove_logo"): ex("UPDATE accounts SET logo=NULL WHERE id=?", acc["id"])
        flash("সেভ হয়েছে ✅", "ok"); return redirect(request.path)
    return render_template("brand.html")

@app.route("/logo/<int:aid>")
def logo(aid):
    a = q1("SELECT logo FROM accounts WHERE id=?", aid)
    if not a or not a["logo"]: abort(404)
    return send_from_directory(UPLOADS, a["logo"], max_age=300)

@app.route("/dashboard/subscription")
@roles("owner")
def subscription():
    pays = qa("SELECT * FROM payments WHERE account_id=? ORDER BY id DESC", g.account["id"])
    kind = g.account["kind"]
    avail = [p for p in PLANS if p["id"] != "trial" and p["kind"] == kind]
    return render_template("subscription.html", pays=pays, avail=avail, periods=PERIODS)

@app.route("/checkout/<pid>", methods=["GET", "POST"])
@roles("owner")
def checkout(pid):
    p = PLAN.get(pid)
    if not p or pid == "trial" or p["kind"] != g.account["kind"]: abort(404)
    period = request.values.get("period", "month")
    if period not in PERIODS: period = "month"
    amount = p["price_m"] if period == "month" else p["price_w"]
    if request.method == "POST":
        trx, sender, method = request.form.get("trx", "").strip(), request.form.get("sender", "").strip(), request.form.get("method")
        if len(trx) < 6 or method not in PAY_NUMBERS or not re.fullmatch(r"01\d{9}", sender):
            flash("ট্রানজেকশন আইডি, পাঠানো নাম্বার ও মাধ্যম ঠিকভাবে দাও।", "err")
        elif q1("SELECT 1 FROM payments WHERE trx=?", trx):
            flash("এই ট্রানজেকশন আইডি আগেই জমা দেওয়া হয়েছে।", "err")
        else:
            ex("INSERT INTO payments(account_id,plan,period,amount,method,trx,sender,status,created_at) VALUES(?,?,?,?,?,?,?,'pending',?)",
               g.account["id"], pid, period, amount, method, trx, sender, now())
            flash("পেমেন্টের তথ্য জমা হয়েছে। যাচাই হলেই প্ল্যান চালু হবে (সাধারণত কয়েক ঘণ্টায়)।", "ok")
            return redirect("/dashboard/subscription")
    return render_template("checkout.html", p=p, period=period, amount=amount, periods=PERIODS, pay_numbers=PAY_NUMBERS)

# ====================================================================
#  ৮. সুপার অ্যাডমিন প্যানেল (শুধু তোমার জন্য)
# ====================================================================
def apply_payment(pay):
    acc = q1("SELECT * FROM accounts WHERE id=?", pay["account_id"])
    days = PERIODS[pay["period"]][1]
    base = acc["expires_at"] if (acc["status"] == "active" and acc["expires_at"] > now() and acc["plan"] == pay["plan"]) else now()
    ex("UPDATE accounts SET plan=?,status='active',expires_at=? WHERE id=?", pay["plan"], base + days * 86400, acc["id"])
    ex("UPDATE payments SET status='paid',decided_at=? WHERE id=?", now(), pay["id"])

@app.route("/admin")
@roles("admin")
def admin():
    qs = request.args.get("q", "").strip(); flt = request.args.get("f", "")
    accs = qa("SELECT a.*,(SELECT COUNT(*) FROM users u WHERE u.account_id=a.id AND u.role IN ('student','owner')) n_st,"
              "(SELECT COUNT(*) FROM users u WHERE u.account_id=a.id AND u.role='teacher') n_t,"
              "(SELECT username FROM users u WHERE u.account_id=a.id AND u.role='owner' LIMIT 1) owner_user "
              "FROM accounts a ORDER BY a.id DESC")
    def state(a):
        if a["status"] == "suspended": return "suspended"
        if a["expires_at"] <= now(): return "expired"
        return a["status"]
    rows = []
    for a in accs:
        d = dict(a); d["state"] = state(a)
        if qs and qs.lower() not in (a["name"] + (a["phone"] or "") + (a["owner_user"] or "")).lower(): continue
        if flt and d["state"] != flt: continue
        rows.append(d)
    allst = [state(a) for a in accs]
    stats = dict(total=len(accs), trial=allst.count("trial"), active=allst.count("active"), expired=allst.count("expired"),
                 suspended=allst.count("suspended"),
                 revenue=q1("SELECT COALESCE(SUM(amount),0) s FROM payments WHERE status='paid'")["s"],
                 month=q1("SELECT COALESCE(SUM(amount),0) s FROM payments WHERE status='paid' AND decided_at>?", now() - 30 * 86400)["s"],
                 users=q1("SELECT COUNT(*) c FROM users WHERE role!='admin'")["c"])
    pend = qa("SELECT p.*,a.name aname FROM payments p JOIN accounts a ON a.id=p.account_id WHERE p.status='pending' ORDER BY p.id")
    return render_template("admin.html", rows=rows, stats=stats, pend=pend, qs=qs, flt=flt)

@app.route("/admin/payment/<int:pid>", methods=["POST"])
@roles("admin")
def admin_payment(pid):
    pay = q1("SELECT * FROM payments WHERE id=?", pid)
    if not pay or pay["status"] != "pending": abort(404)
    if request.form.get("act") == "approve": apply_payment(pay); flash("অনুমোদিত, প্ল্যান চালু হয়েছে ✅", "ok")
    else: ex("UPDATE payments SET status='rejected',decided_at=? WHERE id=?", now(), pid); flash("বাতিল করা হয়েছে।", "warn")
    return redirect(request.referrer or "/admin")

@app.route("/admin/account/<int:aid>", methods=["GET", "POST"])
@roles("admin")
def admin_account(aid):
    acc = q1("SELECT * FROM accounts WHERE id=?", aid)
    if not acc: abort(404)
    if request.method == "POST":
        act = request.form.get("act")
        if act == "plan" and request.form.get("plan") in PLAN:
            ex("UPDATE accounts SET plan=?,status=CASE WHEN ?='trial' THEN 'trial' ELSE 'active' END WHERE id=?",
               request.form["plan"], request.form["plan"], aid)
        elif act == "extend":
            d = int(request.form.get("days", 7)); base = max(acc["expires_at"], now())
            ex("UPDATE accounts SET expires_at=? WHERE id=?", base + d * 86400, aid)
        elif act == "suspend": ex("UPDATE accounts SET status='suspended' WHERE id=?", aid)
        elif act == "unsuspend":
            ex("UPDATE accounts SET status=? WHERE id=?", "trial" if acc["plan"] == "trial" else "active", aid)
        elif act == "delete":
            ex("DELETE FROM accounts WHERE id=?", aid); flash("অ্যাকাউন্ট মুছে ফেলা হয়েছে।", "warn"); return redirect("/admin")
        elif act == "resetpw":
            o = q1("SELECT id FROM users WHERE account_id=? AND role='owner'", aid); npw = str(secrets.randbelow(900000) + 100000)
            ex("UPDATE users SET password_hash=? WHERE id=?", generate_password_hash(npw), o["id"]); ex("DELETE FROM sessions WHERE user_id=?", o["id"])
            flash("নতুন পাসওয়ার্ড: " + npw + " (মালিককে জানিয়ে দাও)", "ok")
        flash("হয়ে গেছে ✅", "ok"); return redirect(request.path)
    s, t = seat_counts(acc)
    users = qa("SELECT * FROM users WHERE account_id=? ORDER BY role,name", aid)
    pays = qa("SELECT * FROM payments WHERE account_id=? ORDER BY id DESC", aid)
    return render_template("admin_account.html", a=acc, s=s, t=t, users=users, pays=pays, plans=PLANS)

# ====================================================================
#  ৯. এরর পেজ
# ====================================================================
@app.errorhandler(403)
def e403(e): return render_template("error.html", code=403, msg="এই পেজে তোমার ঢোকার অনুমতি নেই।"), 403
@app.errorhandler(404)
def e404(e): return render_template("error.html", code=404, msg="পেজটি খুঁজে পাওয়া যায়নি।"), 404
@app.errorhandler(400)
def e400(e): return render_template("error.html", code=400, msg=getattr(e, "description", "ভুল অনুরোধ।")), 400
@app.errorhandler(413)
def e413(e): return render_template("error.html", code=413, msg="ফাইল বেশি বড় (সর্বোচ্চ ২ MB)।"), 413

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=bool(os.environ.get("DEBUG")))
