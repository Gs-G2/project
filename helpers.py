import random
from string import digits, ascii_letters
from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL

# Constants
# Dice
MAX_AMOUNT_OF_DICE = 3

# Slug
BEING_USED = []
SLUG_SIZE = 6
CHARACTERS = ascii_letters + digits

db = SQL("sqlite:///project.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def is_banned(user_id, room_id):
    try:
        rows = db.execute("SELECT * FROM banned WHERE user_id = ? AND room_id = ?", user_id, room_id)
        return True if len(rows) > 0 else False
    except:
        return False


def get_users(room_id):
    try:
        owner = db.execute("SELECT username, users.id AS user_id FROM rooms INNER JOIN users ON users.id == rooms.owner_id WHERE rooms.id = ?", room_id)
        rows = db.execute("SELECT username, users.id AS user_id FROM active INNER JOIN users ON users.id == active.user_id WHERE room_id = ?", room_id)
        return {"owner": {"username": owner[0]["username"], "id": owner[0]["user_id"]}, "users": {row["user_id"]: row["username"] for row in rows}}
    except:
        return False


def roll(type="D6", amount=1):
    if not type in ["D4", "D6", "D8", "D10", "D12", "D20", "D100"]:
        raise ValueError("Dice not allowed")
    
    if not amount in range(1, MAX_AMOUNT_OF_DICE + 1):
        raise ValueError(f"Amount must be between 1 and {MAX_AMOUNT_OF_DICE}")

    MAX = int(type.replace("D", ""))
    return [random.randint(1, MAX) for _ in range(amount)]


def generate_random_slug():
    slug = ""
    for _ in range(SLUG_SIZE):
        slug += str(random.choice(CHARACTERS))

    if slug in BEING_USED:
        generate_random_slug()
        return

    BEING_USED.append(slug)
    return slug


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code