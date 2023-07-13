# dices.

#### Video Demo: <https://youtu.be/8-rU0GQsoiM>

#### Description:

Dices is a web application where users can join virtual rooms, chat with your friends and roll a dice for any game.

We implemented a system to connect bidirectionally with the user during his stay on the room page using a WebSocket (flask_socketio), so when the user join on a room after a several validations, it connect with our server and the user can see in real time changes on the room's database and the changes appears to the other people on the same room too, with this system we create a chat, system to update in real time users connected, and the roll dice's system and the main room manager, who update the database and the connection with websocket by his own function "join_room" and "leave_room" to emit events to only room conected users. Underneath the hood, we use a javascript code with the socketio library on client and on server (flask_socketio) to emit events and update the page. There are also a page to register and login using a session system provided by flask_session library.

We use a function to create a page slug using the string and random libraries to generate a unique slug with six random digits to make the room code to be accessed later by the admin friends, and a function to roll a dice and help on a main function wrote on the server.

We use a database to control the flow of the website, we decided to use three tables to do this: "rooms", "active" and "banned", in the first, we store all the rooms with at least one user, the "active" table store the user's room with a constraint to give him access to only one room and necessarily a room registered on table "rooms", the "banned" table store user's who cannot have access to a room with the constraint of a room registered on the table "rooms" too and a extra table to store user's register information with a hashed password to protect user's privacy in case of leak database information.

We design the workflow to show the user a main page requesting the user to logon to use the server function, so to create a room the user needs to input a password, after this the server will generate a slug with a function and will put thim in the room with admin permission to ban any user in that room, the user can share the code to other friend to give them access, when they enter, the users table will update to everyone online and after that they will can chat with each other and roll dices together.

Thanks to the team behind CS50 and a special thanks to David Malan!
**This was CS50**

Made by [**caio_farias21**](https://github.com/caio-farias21) (github) and [**Gs-G2**](https://github.com/Gs-G2) (github)
