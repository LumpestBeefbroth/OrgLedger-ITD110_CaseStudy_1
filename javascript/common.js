let api = "";

const currencyRates = {
  "$": 1,
  "€": 0.92,
  "₱": 57,
  "¥": 155
};

function convertAmount(amount, from = "$", to = null) {
  if (!to) to = localStorage.getItem("currency") || "$";
  if (from === to) return amount;
  const usdAmount = amount / (currencyRates[from] || 1);
  return usdAmount * (currencyRates[to] || 1);
}

function logout() {
  const theme = localStorage.getItem("theme");
  localStorage.clear();
  if (theme) localStorage.setItem("theme", theme);
  window.location.href = "login.html";
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("overlay");
  if (sidebar) sidebar.classList.toggle("active");
  if (overlay) overlay.classList.toggle("active");
}

function applyDarkModeFromStorage() {
  const isDark = localStorage.getItem("theme") === "dark";
  document.body.classList.toggle("dark", isDark);
  const darkModeToggle = document.getElementById("darkModeToggle");
  if (darkModeToggle) {
    darkModeToggle.checked = isDark;
    darkModeToggle.onchange = function() {
      if (this.checked) {
        localStorage.setItem("theme", "dark");
        document.body.classList.add("dark");
      } else {
        localStorage.setItem("theme", "light");
        document.body.classList.remove("dark");
      }
    };
  }
}

document.addEventListener("DOMContentLoaded", applyDarkModeFromStorage);

document.addEventListener("DOMContentLoaded", () => {
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      sidebar.classList.toggle("active");
    });
  }
  document.addEventListener("click", function(event) {
    if (sidebar && sidebar.classList.contains("active")) {
      if (!sidebar.contains(event.target) && event.target !== sidebarToggle) {
        sidebar.classList.remove("active");
      }
    }
  });
});

document.addEventListener("click", function(event) {
  const sidebar = document.getElementById("sidebar");
  const toggleButton = document.getElementById("sidebarToggle");

  if (sidebar && sidebar.contains(event.target)) return;
  if (toggleButton && event.target === toggleButton) return;
  
  if (sidebar) {
    sidebar.classList.remove("active");
  }
});
