// URL share button
const share = document.getElementById("share");
const shareButton = document.getElementById("share-button");
const shareIcon = document.getElementById("share-icon");

const url = window.location.href.split("/");
share.innerHTML = `<span class="fw-bold">Your room code: </span>${url[
  url.length - 1
].slice(0, 6)}`;

if (navigator.clipboard) {
  shareButton.setAttribute("data-bs-content", "Copied! 🥳");
  shareButton.addEventListener("click", () => {
    window.navigator.clipboard.writeText(url[url.length - 1]);
    shareIcon.classList.remove("bi-clipboard");
    shareIcon.classList.add("bi-clipboard-check-fill");
    shareButton.classList.add("btn-secondary");
    shareButton.classList.remove("btn-outline-secondary");
    setTimeout(() => {
      shareIcon.classList.remove("bi-clipboard-check-fill");
      shareIcon.classList.add("bi-clipboard");
      shareButton.classList.add("btn-outline-secondary");
      shareButton.classList.remove("btn-secondary");
    }, 3000);
  });
} else {
  shareButton.setAttribute("data-bs-content", "Not supported 😢");
}

// Background switcher
const roomBackground = document.getElementById("room_background");
window.addEventListener("resize", () => {
  if (window.innerWidth <= 768) {
    roomBackground.setAttribute(
      "src",
      "../static/images/room_background_mobile.png"
    );
  } else {
    roomBackground.setAttribute("src", "../static/images/room_background.png");
  }
});

// Popover bootstrap dependency
const popoverTriggerList = document.querySelectorAll(
  '[data-bs-toggle="popover"]'
);
const popoverList = [...popoverTriggerList].map(
  (popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl)
);
