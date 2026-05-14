if (document.getElementById("changeUsernameForm")) {
  document.getElementById("changeUsernameForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const newUsername = document.getElementById("newUsername").value.trim();
    const userId = localStorage.getItem("user_id");
    if (!newUsername || !userId) return;

    const res = await fetch(`${api}/user/${userId}/username`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: newUsername })
    });
    if (res.ok) {
      localStorage.setItem("username", newUsername);
      alert("Username updated!");
      document.getElementById("newUsername").value = "";
    } else {
      alert("Failed to update username.");
    }
  });
}

function updateCurrencyDisplay() {
  const currency = localStorage.getItem("currency") || "$";
  const currentCurrencySpan = document.getElementById("currentCurrency");
  if (currentCurrencySpan) {
    currentCurrencySpan.textContent = currency;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const currencySelect = document.getElementById("currencySelect");
  if (currencySelect) {
    currencySelect.value = localStorage.getItem("currency") || "$";
    currencySelect.addEventListener("change", () => {
      localStorage.setItem("currency", currencySelect.value);
      updateCurrencyDisplay();
      if (typeof loadExpenses === "function") loadExpenses();
    });
  }
  updateCurrencyDisplay();
});

function updateAllDisplayedAmounts() {
  const currency = localStorage.getItem("currency") || "$";
  const tbody = document.querySelector("#allExpensesTable tbody");
  if (!tbody) return;
  for (const row of tbody.rows) {
    const amountCell = row.cells[0];
    if (amountCell && amountCell.dataset.usd) {
      const usd = parseFloat(amountCell.dataset.usd);
      const converted = convertAmount(usd, "$", currency);
      amountCell.textContent = `${currency} ${converted.toFixed(2)}`;
    }
  }
}

function updateDarkMode() {
  document.body.classList.toggle("dark", localStorage.getItem("darkMode") === "enabled");
}

async function backupAllExpenses() {
  const userId = localStorage.getItem("user_id");
  if (!userId) return alert("No user logged in.");

  try {
    const res = await fetch(`${api}/export-ledger/${userId}`);
    if (!res.ok) {
      throw new Error("Failed to download backup");
    }
    const jsonData = await res.json();
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "org_ledger_backup.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    alert("JSON Ledger Backup downloaded successfully!");
  } catch (error) {
    alert("Failed to download backup: " + error.message);
  }
}

async function revertAllExpenses() {
  const userId = localStorage.getItem("user_id");
  if (!userId) return;
  if (!confirm("Are you sure you want to revert all expenses to the last backup?")) return;
  const res = await fetch(`${api}/expenses/${userId}/revert`, { method: "POST" });
  if (res.ok) {
    alert("Expenses reverted to last backup!");
  } else {
    alert("Failed to revert expenses.");
  }
}
