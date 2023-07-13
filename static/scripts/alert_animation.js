document.addEventListener("DOMContentLoaded", function () {
  const alertIcon = document.getElementById("alert-icon");
  if (alertIcon) {
    setTimeout(function () {
      document.getElementById("alerts").style.transform =
        "translateY(7.5em) translateX(-50%)";
    }, 500);

    setTimeout(function () {
      document.getElementById("alerts").style.transform =
        "translateY(0) translateX(-50%)";
    }, 5000);
  }
});
