from pywebio import start_server
from pywebio.output import *
from pywebio.input import *
import json, os

# -------------------------
# Files (note: Railway free tier pe ye kabhi reset ho sakte hain)
# -------------------------
USERS_FILE = "users.json"
APPS_FILE = "apps.json"

def load(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

USERS = load(USERS_FILE, [])
APPS = load(APPS_FILE, [])

CURRENT_USER = None

# --------- IMAGES (links yaha paste karna) ----------
LOGO_IMG   = "https://res.cloudinary.com/dzq3n9tyy/image/upload/v1768486626/SmartSelect_20260115_193342_Google_you5ph.jpg"
DONATE_IMG = "https://res.cloudinary.com/dzq3n9tyy/image/upload/v1768486625/SmartSelect_20260115_193503_WhatsApp_qam3nc.jpg"

# ---------------- UI ----------------
def header():
    put_row([
        put_image(LOGO_IMG, width="70px"),
        put_markdown("# **Q-Store**"),
        put_image(DONATE_IMG, width="70px"),
    ], size="20% 60% 20%")

    put_markdown("---")

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
    put_markdown("---")

# ---------------- PAGES ----------------
def home():
    clear()
    header()
    put_markdown("## Welcome to Q-Store")
    put_text("Marketplace for apps & games.")

def store():
    clear()
    header()
    put_markdown("## 🏬 Store")

    if not APPS:
        put_text("No apps available yet.")
        return

    for app in APPS:
        with put_card():
            put_image(app["logo"], width="80px")
            put_markdown(f"### {app['name']}")
            put_text(app["desc"])
            put_text(f"By: {app['company']}")
            put_link("⬇ Download", app["file_link"])

# ---------------- AUTH ----------------
def signup():
    clear()
    header()
    data = input_group("Create Account", [
        input("Company Name", name="company"),
        input("Email", name="email"),
        input("Password", type=PASSWORD, name="password"),
    ])

    if any(u["email"] == data["email"] for u in USERS):
        put_error("Email already exists!")
        return home()

    USERS.append(data)
    save(USERS_FILE, USERS)
    put_success("Account created! Please login.")
    login()

def login():
    global CURRENT_USER
    clear()
    header()

    data = input_group("Login", [
        input("Email", name="email"),
        input("Password", type=PASSWORD, name="password"),
    ])

    user = next((u for u in USERS if u["email"] == data["email"] and u["password"] == data["password"]), None)
    if not user:
        put_error("Wrong credentials!")
        return home()

    CURRENT_USER = user
    dashboard()

def logout():
    global CURRENT_USER
    CURRENT_USER = None
    home()

# ---------------- DASHBOARD ----------------
def dashboard():
    if not CURRENT_USER:
        return login()

    clear()
    header()
    put_markdown("## Developer Dashboard")
    put_button("➕ Add New App", onclick=submit_app)

    my_apps = [a for a in APPS if a["owner"] == CURRENT_USER["email"]]
    if not my_apps:
        put_text("You haven’t added any apps yet.")
        return

    for app in my_apps:
        with put_card():
            put_markdown(f"### {app['name']}")
            put_text(app["desc"])
            put_link("Download", app["file_link"])

# ---------------- SUBMIT APP ----------------
def submit_app():
    if not CURRENT_USER:
        return login()

    clear()
    header()
    put_markdown("""
### Steps  
1. Upload your app file to **Google Drive / Dropbox**  
2. Copy download link  
3. Upload your **logo image** somewhere and copy image link  
""")

    data = input_group("App Details", [
        input("App Name", name="name"),
        textarea("Description", name="desc"),
        input("Version", name="version"),
        input("File Size", name="size"),
        input("Download Link (Drive/Dropbox)", name="file_link"),
        input("Logo Image Link", name="logo"),
    ])

    app = {
        "id": len(APPS) + 1,
        "name": data["name"],
        "desc": data["desc"],
        "version": data["version"],
        "size": data["size"],
        "file_link": data["file_link"],
        "logo": data["logo"],
        "company": CURRENT_USER["company"],
        "owner": CURRENT_USER["email"],
    }

    APPS.append(app)
    save(APPS_FILE, APPS)

    put_success("Your app is now live on Q-Store!")
    dashboard()

# ---------------- MAIN ----------------
def main():
    home()

# -------- Railway needs dynamic PORT --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    start_server(main, port=port, debug=False)
