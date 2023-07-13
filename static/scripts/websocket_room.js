window.onload = () => {
  var socket = io();
  var current_users = [];

  const self_user = document
    .getElementById("username")
    .innerText.replace("\n", "")
    .trim();

  socket.on("connect", () => {
    console.log("Conectado ao servidor");
    document.getElementById("send-button").classList.remove("disabled");
    socket.emit("join");
  });

  socket.on("disconnect", () => {
    document.getElementById("send-button").classList.add("disabled");
    console.log("Desconectado do servidor");
    window.location.reload(true);
  });

  socket.on("user_join", (username) => {
    if (current_users.includes(username)) {
      return;
    }
    document.getElementById(
      "chat"
    ).innerHTML += `<div class="text-muted text-center mb-2"><small>${username} has entered the room</small></div>`;
  });

  socket.on("user_leave", (username) => {
    document.getElementById(
      "chat"
    ).innerHTML += `<div class="text-muted text-center mb-2"><small>${username} has left the room</small></div>`;
  });

  socket.on("users", (users, owner) => {
    document.getElementById("users").innerHTML = "";
    current_users = Object.entries(users).map(([user_id, username]) => {
      return username;
    });
    if (!current_users.includes(self_user)) {
      window.location.reload(true);
    }
    Object.entries(users).forEach(([user_id, username]) => {
      if (user_id == owner["id"]) {
        document.getElementById(
          "users"
        ).innerHTML += `<li class="list-group-item bg-warning fw-bold">${username}</li>`;
        return;
      }
      document.getElementById("users").innerHTML += `
        <li class="list-group-item position-relative w-auto overflow-visible">
          <div class="three-dots position-absolute end-0 mx-2 d-flex align-items-center dropend d-none">
            <button class="btn remove-letter-padding rounded border p-1" type="button" data-bs-toggle="dropdown" aria-expanded="false">
              <i class="bi bi-three-dots"></i>
            </button>
            <ul class="dropdown-menu">
              <li>
                <button class="ban-btn dropdown-item text-danger" type="submit" value="${user_id}">Banir</button>
              </li>
            </ul>
          </div>
          ${username}
        </li>
        `;
    });
    if (owner["username"] == self_user) {
      document.querySelectorAll(".three-dots").forEach((element) => {
        element.classList.remove("d-none");
      });
    }
    document.querySelectorAll(".ban-btn").forEach((element) => {
      element.addEventListener("click", (e) => {
        e.preventDefault();
        socket.emit("ban", element.value);
      });
    });
  });

  socket.on("string_data", (message, username) => {
    const chat = document.getElementById("chat");
    const messageElement = document.createElement("div");
    messageElement.classList.add(
      "mb-2",
      "bg-light",
      "rounded",
      "p-2",
      "w-auto"
    );
    const messageContent = document.createElement("span");
    const messageUser = document.createElement("small");
    messageUser.innerHTML = username;
    messageUser.classList.add("d-block", "text-muted");
    messageElement.appendChild(messageUser);
    messageContent.innerHTML = message;
    messageElement.appendChild(messageContent);
    chat.appendChild(messageElement);
    chat.scrollTop = chat.scrollHeight;
  });
  socket.on("dice_receive", (numbers, username, dice, amount) => {
    const chat = document.getElementById("chat");
    chat.innerHTML += `
        <div class="bg-white border rounded text-danger position-relative my-2">
          <div
            class="bg-danger position-absolute start-0 h-100 rounded-start"
            style="width: 30px"
          ></div>
          <img
            src="../static/images/background_dice_left.png"
            alt="background card"
            class="position-absolute end-0 h-100 py-2 rounded-end d-none d-xl-block"
          />
          <div class="my-auto h-100 p-3 ps-5">
            <div class="mb-2">
              <span class="fw-bold">${username} </span><span>threw a ${dice} - (x${amount})</span>
            </div>
            <span
              class="fw-bold border border-danger-subtle rounded px-3 py-1"
              style="letter-spacing: 0.25em"
            >
              ${numbers.join(" | ")}
            </span>
          </div>
        </div>
      `;
    chat.scrollTop = chat.scrollHeight;
  });

  document.getElementById("chat-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const message = document.getElementById("message").value;
    socket.emit("message_handler", { message: message });
    document.getElementById("message").value = "";
  });

  document.getElementById("exit-button").addEventListener("click", (e) => {
    e.preventDefault();
    socket.emit("leave");
    window.location.href = "/";
  });

  const diceForm = document.getElementById("dices-form");
  diceForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const dice = document.getElementById("dice-select");
    const amount = document.getElementById("amount-select");
    socket.emit(
      "dice_handler",
      dice.options[dice.selectedIndex].value,
      amount.options[amount.selectedIndex].value
    );
  });
};
