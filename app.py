from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import roll, generate_random_slug, apology, login_required, get_users, is_banned
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
from cs50 import SQL

# Flask and Socket
app = Flask(__name__)
socketio = SocketIO(app)


# Session config
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# DB config
db = SQL("sqlite:///project.db")

# On restart
db.execute("DELETE FROM active")
db.execute("DELETE FROM banned")
db.execute("DELETE FROM rooms")

# Constants
MAX_USERS_PER_ROOM = 10


@app.route("/")
def index():
    if session.get("user_id") is None:
        return render_template("index.html")
    
    # Send the user informations of their current room
    room = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])
    return render_template("index.html", actual_room=room if len(room) != 0 else None)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        username = str(request.form.get("username")).strip()
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"], session["username"] = rows[0]["id"], request.form.get("username")

        # Redirect user to home page
        flash(f"Welcome, {request.form.get('username')}")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get("user_id"):
        return redirect("/")
    
    if request.method == "POST":
        # Validate
        # User must provide a username
        if not request.form.get("username"):
            return apology("must provide username", 400)
        
        # User must provide a password
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        
        # User must provide a confirmation
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)
        
        # Password and confirmation must be equal
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must be equal", 400)
        
        # Password must be 4 characters or higher
        if len(request.form.get("password")) < 4:
            return apology("password must be 4 characters or higher", 400)
        
        # gets rows of username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # see if there is no username equal
        if len(rows) != 0:
            return apology("invalid username", 403)
        
        # get variable with username and hashed password
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        # insert username and hashed password in database
        db.execute("INSERT into users (username, hash) VALUES(?, ?)", username, hash)

        # redirect to login page
        return render_template("login.html")
    # renders page
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/enter", methods=["POST"])
@login_required
def enter():
    # Validate
    # User must provide a room code
    if not request.form.get("room_code"):
        return apology("must provide code", 400)
    
    # User must provide a password
    elif not request.form.get("password"):
        return apology("must provide password", 400)
    
    # Password must be 4 characters or higher
    if len(request.form.get("password")) < 4:
        return apology("password must be 4 characters or higher", 400)
    
    # Room code must have 6 characters
    if len(request.form.get("room_code")) != 6:
        return apology("room code has 6 characters", 400)

    # Room must be alphanumeric
    if not str(request.form.get("room_code")).isalnum():
        return apology("room code must be alphanumeric", 400)

    # Check if room exists
    rows = db.execute("SELECT hash FROM rooms WHERE id = ?", request.form.get("room_code"))
    if len(rows) != 1:
        flash("Room not found!")
        return redirect("/")
    
    # Check if user is banned
    if is_banned(session["user_id"], request.form.get("room_code")):
        flash("You are banned from this room")
        return redirect("/")
    
    # Check if room is full
    how_many_users = db.execute("SELECT * FROM active WHERE room_id = ?", request.form.get("room_code"))
    if len(how_many_users) >= MAX_USERS_PER_ROOM:
        flash(f"This room is crowded, max: {MAX_USERS_PER_ROOM} users")
        return redirect("/")

    # Check if password is correct
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Wrong Password!")
        return redirect("/")

    # Check if user is already in a room
    inroom = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])
    if len(inroom) == 1:
        flash("Please, leave your current room")
        return redirect("/")
    
    # Check if has a user in the room
    priority = db.execute("SELECT MAX(priority) AS max FROM active WHERE room_id = ?", request.form.get("room_code"))
    if len(priority) != 1:
        flash("Error")
        return redirect("/")

    # Insert user in the room
    db.execute("INSERT INTO active (room_id, user_id, priority) VALUES (?, ?, ?)", request.form.get("room_code"), session["user_id"], priority[0]["max"] + 1)
    return redirect(f"/room/{request.form.get('room_code')}")


@app.route("/room", methods=["POST"])
@login_required
def initialRoom():
    # Validate
    # User must provide a password
    if not request.form.get("room_password"):
        return apology("must provide password", 400)
    
    # User must provide a confirmation
    elif not request.form.get("confirmation"):
        return apology("must provide confirmation", 400)
    
    # Password and confirmation must be equal
    elif request.form.get("room_password") != request.form.get("confirmation"):
        return apology("password and confirmation must be equal", 400)
    
    # Password must be 4 characters or higher
    if len(request.form.get("room_password")) < 4:
        return apology("password must be 4 characters or higher", 400)

    # User must not be in a room
    inroom = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])
    if len(inroom) == 1:
        flash("Please, leave your current room")
        return redirect("/")

    # Create room
    room_hash = generate_password_hash(request.form.get("room_password"))
    room_slug = generate_random_slug()

    # Insert room and user into database
    try:
        db.execute("INSERT INTO rooms (id, owner_id, hash) VALUES (?, ?, ?)", room_slug, session["user_id"], room_hash)
        db.execute("INSERT INTO active (room_id, user_id, priority) VALUES (?, ?, ?)", room_slug, session["user_id"], 1)
    except:
        flash("You cannot create a room now...")
        return redirect("/")

    return redirect(f"/room/{room_slug}")


@app.route("/room/<id>")
@login_required
def room(id):
    # Validate
    # Room must be 6 characters long
    if len(id) != 6:
        return redirect("/")

    # Room must be alphanumeric
    if not str(id).isalnum():
        return redirect("/")

    # User must be not banned
    if is_banned(session["user_id"], id):
        flash("You're banned from this room!")
        return redirect("/") 

    # User must be in the room
    rows = db.execute("SELECT * FROM active WHERE room_id = ? AND user_id = ?", id, session["user_id"])
    if len(rows) != 1:
        flash("You do not have access from to this room")
        return redirect("/") 

    return render_template("room.html", code=id)


@socketio.on("leave")
@login_required
def on_leave():
    # Validate
    # User must be in a room
    rows = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])

    if len(rows) != 1:
        flash("You aren't in a room")
        return redirect("/")

    # Delete user from active table
    db.execute("DELETE FROM active WHERE user_id = ?", session["user_id"])
    room_id = rows[0]["room_id"]

    # If user was the owner, assign a new owner
    users_in_room = db.execute("SELECT user_id FROM active WHERE room_id = ?", room_id)
    if len(users_in_room) != 0:
        db.execute("UPDATE rooms SET owner_id = ? WHERE id = ?", db.execute("SELECT user_id FROM active WHERE room_id = ? AND priority = ?", room_id, db.execute("SELECT MIN(priority) AS priority FROM active WHERE room_id = ?", room_id)[0]["priority"])[0]["user_id"], room_id)
    # If user was the last one, delete room
    else:
        db.execute("DELETE FROM banned WHERE room_id = ?", room_id)
        db.execute("DELETE FROM rooms WHERE id = ?", room_id)
        close_room(room_id)

    # Leave room
    leave_room(room_id)
    socketio.emit("user_leave", session["username"], to=room_id)

    # Update users list
    if result := get_users(room_id):
        socketio.emit("users", (result["users"], result["owner"]), to=room_id)


@socketio.on("ban")
@login_required
def on_ban(user_id):
    # Validation
    # User requesting is admin in one of rooms
    is_admin = db.execute("SELECT id AS room_id FROM rooms WHERE owner_id = ?", session["user_id"])
    if len(is_admin) != 1:
        return apology("not admin", 403)

    # User who will be banned is in a room
    banned_user_room = db.execute("SELECT room_id FROM active WHERE user_id = ?", user_id)
    if len(banned_user_room) != 1:
        return apology("user isn't in a room", 403)

    # User who will banned and admin are in the same room
    admin_room = is_admin[0]["room_id"]
    if banned_user_room[0]["room_id"] != admin_room:
        return apology("different room ban command", 403)

    # User who will be banned isn't admin
    if session["user_id"] == user_id:
        return apology("can't ban yourself", 403)

    # Ban user
    db.execute("INSERT INTO banned (user_id, room_id) VALUES (?, ?)", user_id, db.execute("SELECT room_id FROM active WHERE user_id = ?", user_id)[0]["room_id"])
    db.execute("DELETE FROM active WHERE user_id = ?", user_id)

    # Send via WebSocket the leave message and update users list
    username_banned = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
    socketio.emit("user_leave", username_banned, to=admin_room)
    if result := get_users(admin_room):
        socketio.emit("users", (result["users"], result["owner"]), to=admin_room)



@socketio.on('join')
@login_required
def on_join():
    # Validate
    # User must not be in a room
    rows = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])
    if len(rows) == 0:
        return apology("not in a room", 403)
    
    # User must not be banned
    if is_banned(session["user_id"], rows[0]["room_id"]):
        return apology("banned", 400)

    # Join room
    room_id = rows[0]["room_id"]
    join_room(room_id)
    emit("user_join", session["username"], to=room_id)

    # Update users list
    if result := get_users(room_id):
        emit("users", (result["users"], result["owner"]), to=room_id)


@socketio.on('message_handler')
@login_required
def handle_message(data):
    # Validate
    # Message must not be empty
    if data.get("message") is None:
        return apology("must provide message", 400)

    # User must be in a room
    verify_user_in_room = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])
    if len(verify_user_in_room) != 1:
        return apology("not in a room", 403)

    user_room = verify_user_in_room[0]["room_id"]

    # User must not be banned
    if is_banned(session["user_id"], user_room):
        return apology("banned", 400)

    # Send message
    socketio.emit('string_data', (data["message"], session["username"]), to=user_room)


@socketio.on('dice_handler')
@login_required
def handle_dice(dice, amount):
    # Validate
    # User must be in a room
    verify_user_in_room = db.execute("SELECT * FROM active WHERE user_id = ?", session["user_id"])
    if len(verify_user_in_room) != 1:
        return apology("not in a room", 400)

    try:
        numbers = roll(dice, int(amount))
    except ValueError:
        return apology("invalid dice or amount not supported", 403)

    user_room = verify_user_in_room[0]["room_id"]
    socketio.emit('dice_receive', (numbers, session["username"], dice, amount), to=user_room)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")

# This was CS50