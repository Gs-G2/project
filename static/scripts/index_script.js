// Room code button
const roomCode = document.getElementById("room-id");
const roomButton = document.getElementById("room-button");
if (roomButton) roomButton.setAttribute("href", `/room/${roomCode.innerText}`);

// Bootstrap validation
const forms = document.querySelectorAll(".needs-validation");
Array.from(forms).forEach((form) => {
  form.addEventListener(
    "submit",
    (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }

      form.classList.add("was-validated");
    },
    false
  );
});
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]'
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);
