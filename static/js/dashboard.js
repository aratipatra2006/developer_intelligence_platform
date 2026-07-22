// Developer Intelligence Platform — shared front-end behavior.
// Feature cards are now plain links to their own pages (see summary.html,
// health.html, architecture.html, security.html, tech.html, chat.html),
// so no modal wiring is needed here anymore.

document.addEventListener("DOMContentLoaded", () => {
  console.log("Developer Intelligence Platform — page ready");
});

// Lightweight toast helper, kept in case any page needs a transient notice
// (e.g. "copied to clipboard"). Not used by the current pages.
function showToast(message, duration = 2500) {
  let toast = document.getElementById("app-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "app-toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("is-visible"), duration);
}