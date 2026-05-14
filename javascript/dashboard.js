let categories = [];
let expensesData = [];
let selectedCategories = [];
let modifyModeActive = false;
let originalExpense = {};

if (document.getElementById("user")) {
  const user = localStorage.getItem("username");
  if (!user) window.location.href = "login.html";
  document.getElementById("user").textContent = user;

  loadCategories();
  loadExpenses();

  const expenseForm = document.getElementById("expenseForm");
  expenseForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const selectedCheckboxes = document.querySelectorAll('input[name="categoryCheckbox"]:checked');
    const categoryIds = Array.from(selectedCheckboxes).map(cb => cb.value);
    
    if (categoryIds.length === 0) {
      alert("❌ Please select at least one category before adding an expense.");
      return;
    }
    
    const amount = document.getElementById("amount").value.trim();
    const description = document.getElementById("description").value.trim();
    const date = document.getElementById("date").value.trim();
    const transactionType = document.getElementById("transactionType").value.trim();
    const orNumber = document.getElementById("orNumber").value.trim();
    
    if (!amount || !description || !date || !transactionType) {
      alert("❌ Please fill in all expense fields.");
      return;
    }
    
    const currency = localStorage.getItem("currency") || "$";
    const inputAmount = parseFloat(amount);
    const amountInUSD = inputAmount / (currencyRates[currency] || 1);

    const categoryId = categoryIds[0];

    const res = await fetch(`${api}/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: localStorage.getItem("user_id"),
        category_id: categoryId,
        amount: inputAmount,
        description: description,
        date: date,
        transaction_type: transactionType,
        or_number: orNumber
      })
    });
    if (res.ok) {
      const savedCategories = [...selectedCategories];
      
      expenseForm.reset();
      alert("✅ Expense added successfully!");
      
      await loadCategories();
      await loadExpenses();
      
      selectedCategories = savedCategories;
      const checkboxes = document.querySelectorAll('input[name="categoryCheckbox"]');
      checkboxes.forEach(cb => {
        cb.checked = savedCategories.includes(cb.value);
      });
    } else {
      alert("❌ Failed to add expense.");
    }
  });

  const searchBar = document.getElementById("searchBar");
  if (searchBar) searchBar.addEventListener("keyup", searchExpenses);
}

const expSearch = document.getElementById("expenseSearch");
const expSort = document.getElementById("expenseSort");
if (expSearch) expSearch.addEventListener("input", loadExpenses);
if (expSort) expSort.addEventListener("change", loadExpenses);

const categorySearch = document.getElementById("categorySearch");
if (categorySearch) categorySearch.addEventListener("input", loadCategories);

const categorySort = document.getElementById("categorySort");
if (categorySort) categorySort.addEventListener("change", loadCategories);

async function loadCategories() {
  const userId = localStorage.getItem("user_id");
  const res = await fetch(`${api}/categories/${userId}`);
  if (!res.ok) return;
  categories = await res.json();

  const searchValue = (document.getElementById("categorySearch")?.value || "").toLowerCase();
  const sortValue = document.getElementById("categorySort")?.value || "recent";

  let filtered = categories.filter(cat =>
    cat.name.toLowerCase().includes(searchValue)
  );

  if (sortValue === "az") {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortValue === "recent") {
    filtered.sort((a, b) => b._id.localeCompare(a._id));
  } else if (sortValue === "oldest") {
    filtered.sort((a, b) => a._id.localeCompare(b._id));
  } else if (sortValue === "recently_modified") {
    filtered.sort((a, b) => new Date(b.modified_at || 0) - new Date(a.modified_at || 0));
  } else if (sortValue === "oldest_modified") {
    filtered.sort((a, b) => new Date(a.modified_at || 0) - new Date(b.modified_at || 0));
  }

  const categoryList = document.getElementById("categoryList");
  if (!categoryList) return;
  categoryList.innerHTML = `
    <li style="list-style:none;">
      <button class="all-categories-btn" onclick="selectAllCategories()"><span class="material-symbols-outlined">category</span> All Categories</button>
    </li>
  `;
  filtered.forEach(cat => {
    const isChecked = selectedCategories.includes(cat._id) ? 'checked' : '';
    categoryList.innerHTML += `
      <li style="list-style:none;">
        <label style="width:100%;display:flex;align-items:center;">
          <input type="checkbox" name="categoryCheckbox" value="${cat._id}" ${isChecked} onchange="updateSelectedCategories()">
          <span style="flex:1;">${cat.name}</span>
        </label>
      </li>
    `;
  });
}

function selectAllCategories() {
  selectedCategories = [];
  const checkboxes = document.querySelectorAll('input[name="categoryCheckbox"]');
  checkboxes.forEach(cb => cb.checked = false);
  loadExpenses();
}

function updateSelectedCategories() {
  const checked = document.querySelectorAll('input[name="categoryCheckbox"]:checked');
  selectedCategories = Array.from(checked).map(cb => cb.value);
  loadExpenses();
}

async function deleteSelectedCategory() {
  const checked = document.querySelectorAll('input[name="categoryCheckbox"]:checked');
  if (checked.length === 0) {
    alert("Select at least one category to delete.");
    return;
  }
  
  const categoryIds = Array.from(checked).map(cb => cb.value);
  const categoryNames = Array.from(checked).map(cb => cb.parentElement.querySelector('span').textContent).join(', ');
  
  if (!confirm(`Are you sure you want to delete ${categoryIds.length} categor${categoryIds.length > 1 ? 'ies' : 'y'} (${categoryNames})? All their expenses will be unassigned or deleted.`)) return;
  
  let deletedCount = 0;
  let failedCount = 0;
  
  for (const categoryId of categoryIds) {
    const res = await fetch(`${api}/categories/${categoryId}`, { method: "DELETE" });
    const data = await res.json();
    if (res.ok) {
      deletedCount++;
      selectedCategories = selectedCategories.filter(id => id !== categoryId);
    } else {
      failedCount++;
    }
  }
  
  if (failedCount === 0) {
    alert(`✅ Successfully deleted ${deletedCount} categor${deletedCount > 1 ? 'ies' : 'y'}!`);
  } else {
    alert(`⚠️ Deleted ${deletedCount} categor${deletedCount > 1 ? 'ies' : 'y'}, but ${failedCount} failed.`);
  }
  
  loadCategories();
  loadExpenses();
}

async function addCategory() {
  const name = document.getElementById("newCategoryName").value.trim();
  if (!name) {
    alert("Category name cannot be empty.");
    return;
  }
  const userId = localStorage.getItem("user_id");
  const res = await fetch(`${api}/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, user_id: userId })
  });
  if (res.ok) {
    document.getElementById("newCategoryName").value = "";
    loadCategories();
  } else {
    alert("Failed to add category.");
  }
}

async function loadExpenses() {
  const userId = localStorage.getItem("user_id");
  const res = await fetch(`${api}/expenses/${userId}`);
  if (!res.ok) return;

  expensesData = await res.json();
  const tbody = document.querySelector("#expensesTable tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (modifyModeActive) originalExpense = {};

  const searchValue = (document.getElementById("expenseSearch")?.value || "").toLowerCase();
  const sortValue = document.getElementById("expenseSort")?.value || "recent";
  const currency = localStorage.getItem("currency") || "$";

  let filtered = selectedCategories.length > 0
    ? expensesData.filter(exp => selectedCategories.includes(exp.category_id))
    : expensesData;

  filtered = filtered.filter(exp =>
    (exp.description || "").toLowerCase().includes(searchValue) ||
    (exp.amount + "").includes(searchValue) ||
    (exp.date || "").includes(searchValue)
  );

  if (sortValue === "az") {
    filtered.sort((a, b) => (a.description || "").localeCompare(b.description || ""));
  } else if (sortValue === "recent") {
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
  } else if (sortValue === "oldest") {
    filtered.sort((a, b) => new Date(a.date) - new Date(b.date));
  } else if (sortValue === "recently_modified") {
    filtered.sort((a, b) => new Date(b.modified_at || b.date || 0) - new Date(a.modified_at || a.date || 0));
  } else if (sortValue === "oldest_modified") {
    filtered.sort((a, b) => new Date(a.modified_at || a.date || 0) - new Date(b.modified_at || b.date || 0));
  }

  let totalIncome = 0;
  let totalExpense = 0;
  expensesData.forEach(exp => {
    if (exp.transaction_type === "Income") {
      totalIncome += exp.amount;
    } else {
      totalExpense += exp.amount;
    }
  });
  const currentBalance = totalIncome - totalExpense;
  document.getElementById("walletBalance").textContent = '₱' + currentBalance.toFixed(2);
  document.getElementById("walletIncome").textContent = '₱' + totalIncome.toFixed(2);
  document.getElementById("walletExpense").textContent = '₱' + totalExpense.toFixed(2);

  filtered.forEach(exp => {
    if (modifyModeActive && !originalExpense[exp._id]) {
      originalExpense[exp._id] = { ...exp };
    }
    let dateValue = exp.date;
    let dateInputValue = "";
    if (dateValue) {
      const d = new Date(dateValue);
      if (!isNaN(d)) {
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        const yyyy = d.getFullYear();
        dateValue = `${mm}-${dd}-${yyyy}`;
        dateInputValue = `${yyyy}-${mm}-${dd}`;
      } else {
        dateValue = "";
        dateInputValue = "";
      }
    }
    tbody.innerHTML += `
      <tr data-id="${exp._id}">
        <td>${modifyModeActive ? `<input type="text" value="${exp.description}" id="description-${exp._id}">` : exp.description}</td>
        <td>${exp.transaction_type === "Income" ? `<span class="badge-income">Income</span>` : `<span class="badge-expense">Expense</span>`}</td>
        <td>${exp.or_number || '<span style="color:#999; font-size:0.8em;">N/A</span>'}</td>
        <td>${modifyModeActive ? `<input type="number" value="${exp.amount}" id="amount-${exp._id}">` : `₱${Number(exp.amount).toFixed(2)}`}</td>
        <td>${modifyModeActive ? `<input type="date" value="${dateInputValue}" id="date-${exp._id}">` : dateValue}</td>
        <td class="actions-cell">
          ${modifyModeActive ? `
            <input type="checkbox" class="delete-checkbox" data-id="${exp._id}">
            <button class="revert-button action-btn" onclick="revertExpense('${exp._id}')" title="Revert"><span class="material-symbols-outlined">undo</span></button>
          ` : `
            <button class="delete-button action-btn" onclick="deleteExpense('${exp._id}')" title="Delete"><span class="material-symbols-outlined">delete</span></button>
          `}
        </td>
      </tr>
    `;
  });
}

function toggleModifyMode(reset = false) {
  modifyModeActive = reset ? false : !modifyModeActive;
  document.getElementById("modifyTableButton").style.display = modifyModeActive ? "none" : "inline-block";
  document.getElementById("saveChangesButton").style.display = modifyModeActive ? "inline-block" : "none";
  document.getElementById("cancelModifyButton").style.display = modifyModeActive ? "inline-block" : "none";
  document.getElementById("deleteSelectedButton").style.display = modifyModeActive ? "inline-block" : "none";
  loadExpenses();
}

async function saveAllModifications() {
  const rows = document.querySelectorAll("#expensesTable tbody tr");
  for (const row of rows) {
    const expenseId = row.getAttribute("data-id");
    const amountInput = document.getElementById(`amount-${expenseId}`);
    const descriptionInput = document.getElementById(`description-${expenseId}`);
    const dateInput = document.getElementById(`date-${expenseId}`);
    if (!amountInput || !descriptionInput || !dateInput) continue;

    const updatedExpense = {
      id: expenseId,
      amount: parseFloat(amountInput.value),
      description: descriptionInput.value,
      date: dateInput.value
    };

    await fetch(`${api}/expenses/${updatedExpense.id}/backup`, { method: "POST" });

    const res = await fetch(`${api}/expenses/${updatedExpense.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedExpense)
    });

    const data = await res.json();
    if (!res.ok) {
      alert(`Failed to update expense ${updatedExpense.id}: ${data.error}`);
      return;
    }
  }

  alert("Modifications saved successfully!");
  loadExpenses();
  toggleModifyMode(true);
}

function cancelModifyMode() {
  toggleModifyMode(true);
}

async function revertExpense(expenseId) {
  const res = await fetch(`${api}/expenses/${expenseId}/restore`, { method: "PUT" });
  const data = await res.json();
  if (res.ok) {
    alert(data.message || "Expense reverted to last backup!");
    loadExpenses();
  } else {
    alert(data.error || "Failed to revert expense.");
  }
}

async function deleteSelectedExpenses() {
  const selectedExpenses = Array.from(document.querySelectorAll(".delete-checkbox:checked"))
    .map(checkbox => checkbox.dataset.id);

  if (selectedExpenses.length === 0) {
    alert("Select expenses to delete.");
    return;
  }

  if (!confirm(`Are you sure you want to delete ${selectedExpenses.length} expenses?`)) return;

  for (const expenseId of selectedExpenses) {
    await fetch(`${api}/expenses/${expenseId}`, { method: "DELETE" });
  }

  alert("Selected expenses deleted successfully!");
  loadExpenses();
}

async function deleteExpense(expenseId) {
  if (!confirm("Are you sure you want to delete this expense?")) return;

  const res = await fetch(`${api}/expenses/${expenseId}`, { method: "DELETE" });
  const data = await res.json();
  
  if (!res.ok) {
    alert(`Failed to delete expense: ${data.error}`);
    return;
  }

  alert("Expense deleted successfully!");
  loadExpenses();
}

async function viewAllExpenses() {
  const res = await fetch(`${api}/expenses/${localStorage.getItem("user_id")}`);
  if (!res.ok) {
    return;
  }

  const expenses = await res.json();
  const tbody = document.querySelector("#allExpensesTable tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const currency = localStorage.getItem("currency") || "$";
  for (const exp of expenses) {
    const converted = convertAmount(exp.amount, "$", currency);
    tbody.innerHTML += `
      <tr>
        <td>${exp.description || ""}</td>
        <td data-usd="${exp.amount}">${currency} ${converted.toFixed(2)}</td>
        <td>${exp.date}</td>
      </tr>
    `;
  }
}
