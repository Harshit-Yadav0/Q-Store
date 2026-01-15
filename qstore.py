from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import set_env
import os, json

# ---------------- CONFIG ----------------
LOGO_IMG = "https://res.cloudinary.com/dzq3n9tyy/image/upload/v1768486626/SmartSelect_20260115_193342_Google_you5ph.jpg"     # change later
DONATE_IMG = "https://res.cloudinary.com/dzq3n9tyy/image/upload/v1768486625/SmartSelect_20260115_193503_WhatsApp_qam3nc.jpg"   # change later

USERS_FILE = "users.json"
APPS_FILE = "apps.json"

CURRENT_USER = None

# ---------------- UTILS ----------------
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

users = load_json(USERS_FILE)
apps = load_json(APPS_FILE)

# ---------------- THEME ----------------
def load_theme():
    put_html("""
    <style>
    body {
        background: linear-gradient(135deg, #0f172a, #020617);
        color: #e5e7eb;
        font-family: 'Segoe UI', sans-serif;
    }
    h1,h2,h3 { color:#a5b4fc; }
    a { color:#38bdf8 !important; font-weight:600; }

    .pywebio-button button{
        background: linear-gradient(135deg,#7c3aed,#3b82f6);
        border:none;border-radius:999px;
        padding:8px 18px;color:white;
        font-weight:600;
        box-shadow:0 4px 12px rgba(0,0,0,.3);
    }
    .pywebio-button button:hover{
        background: linear-gradient(135deg,#9333ea,#2563eb);
        transform:translateY(-2px);
    }

    .card{
        background:rgba(255,255,255,0.04);
        border-radius:18px;
        padding:16px;margin-bottom:14px;
        box-shadow:0 10px 25px rgba(0,0,0,.25);
        backdrop-filter:blur(6px);
    }

    input,textarea,select{
        background:#020617 !important;
        border:1px solid #1e293b !important;
        color:#e5e7eb !important;
        border-radius:10px !important;
    }

    .navbar{
        background:rgba(2,6,23,.9);
        padding:12px 16px;
        border-radius:18px;
        box-shadow:0 8px 20px rgba(0,0,0,.4);
        margin-bottom:12px;
    }

    .brand{
        font-size:28px;font-weight:800;
        background:linear-gradient(90deg,#22d3ee,#a78bfa,#f472b6);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    }
    </style>
    """)

# ---------------- UI ----------------
def header():
    load_theme()
    put_html('<div class="navbar">')
    put_row([
        put_image(LOGO_IMG, width="60px"),
        put_markdown('<span class="brand">Q-Store</span>'),
        put_image(DONATE_IMG, width="60px"),
    ], size="20% 60% 20%")

    if CURRENT_USER:
        put_text(f"👤 {CURRENT_USER['company']} | {CURRENT_USER['email']}")
        put_row([
            put_button("Home", onclick=home),
            put_button("Store", onclick=store),
            put_button("Dashboard", onclick=dashboard),
            put_button("Logout", onclick=logout),
        ])
    else:
        put_row([
            put_button("Home", onclick=home),
            put_button("Store", onclick=store),
            put_button("Login", onclick=login),
            put_button("Sign Up", onclick=signup),
        ])
    put_html("</div>")

# ---------------- PAGES ----------------
def home():
    clear()
    header()
    put_html("""
    <div style="text-align:center;padding:40px 10px;">
      <h1 style="font-size:48px;">Welcome to <span class="brand">Q-Store</span></h1>
      <p style="font-size:18px;color:#c7d2fe;">
        A colorful home for indie apps & games 🚀
      </p>
    </div>
    """)

def store():
    clear()
    header()
    put_markdown("## 🛍 Store")

    if not apps:
        put_text("No apps yet. Be the first to upload!")
        return

    for app in apps:
        put_html('<div class="card">')
        put_image(app["logo"], width="90px")
        put_markdown(f"### {app['name']}")
        put_text(app["desc"])
        put_text(f"By: {app['company']}")
        put_link("⬇ Download", app["file_link"])
        put_html('</div>')

def signup():
    clear()
    header()

    data = input_group("Create Account", [
        input("Email", name="email"),
        input("Password", name="password", type=PASSWORD),
        input("Company Name", name="company"),
    ])

    for u in users:
        if u["email"] == data["email"]:
            toast("Email already exists", color="error")
            return

    users.append(data)
    save_json(USERS_FILE, users)
    toast("Account created! Now login.", color="success")
    login()

def login():
    global CURRENT_USER
    clear()
    header()

    data = input_group("Login", [
        input("Email", name="email"),
        input("Password", name="password", type=PASSWORD),
    ])

    for u in users:
        if u["email"] == data["email"] and u["password"] == data["password"]:
            CURRENT_USER = u
            toast("Logged in!", color="success")
            dashboard()
            return

    toast("Invalid credentials", color="error")

def logout():
    global CURRENT_USER
    CURRENT_USER = None
    home()

def dashboard():
    if not CURRENT_USER:
        login()
        return

    clear()
    header()
    put_markdown("## 📦 Developer Dashboard")

    data = input_group("Upload App", [
        input("App Name", name="name"),
        textarea("Description", name="desc"),
        input("App File Link (Drive/Dropbox)", name="file_link"),
        input("App Logo Image URL", name="logo"),
    ])

    new_app = {
        "name": data["name"],
        "desc": data["desc"],
        "file_link": data["file_link"],
        "logo": data["logo"],
        "company": CURRENT_USER["company"]
    }

    apps.append(new_app)
    save_json(APPS_FILE, apps)
    toast("App uploaded successfully!", color="success")
    store()

# ---------------- MAIN ----------------
def main():
    set_env(title="Q-Store", output_animation=False)
    home()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    start_server(main, port=port, debug=False)
