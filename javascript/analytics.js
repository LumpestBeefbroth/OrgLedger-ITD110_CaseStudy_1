let categoryChart = null;
let trendChart = null;
let analyticsData = null;



if (document.getElementById("username")) {
  const user = localStorage.getItem("username");
  if (!user) window.location.href = "login.html";
  document.getElementById("user").textContent = user;
  document.getElementById("username").textContent = user;

  loadAnalytics();
}

async function loadAnalytics() {
  const userId = localStorage.getItem("user_id");
  try {
    const res = await fetch(`${api}/analytics/${userId}`);
    if (!res.ok) {
      return;
    }
    
    analyticsData = await res.json();
    displayStatistics();
    displayCategoryChart();
    displayTrendChart();
    displayCategoryTable();
  } catch (error) {
    alert("Failed to load analytics data");
  }
}

function displayStatistics() {
  if (!analyticsData || !analyticsData.statistics) return;

  const stats = analyticsData.statistics;
  const currency = localStorage.getItem("currency") || "₱";

  document.getElementById("netBalance").textContent = `${currency}${Number(stats.net_balance || 0).toFixed(2)}`;
  document.getElementById("totalIncome").textContent = `${currency}${Number(stats.total_income || 0).toFixed(2)}`;
  document.getElementById("totalExpense").textContent = `${currency}${Number(stats.total_expense || 0).toFixed(2)}`;
  document.getElementById("totalCount").textContent = `${stats.count || 0}`;
}

function displayCategoryChart() {
  if (!analyticsData || !analyticsData.category_totals) return;

  const categoryChartCanvas = document.getElementById("categoryChart");
  const categories = analyticsData.category_totals;

  const labels = categories.map(cat => cat._id.category_name || "Uncategorized");
  const data = categories.map(cat => cat.total);
  const colors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
    '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
  ];

  if (categoryChart) categoryChart.destroy();

  categoryChart = new Chart(categoryChartCanvas, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: '#ffffff',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

function displayTrendChart() {
  if (!analyticsData || !analyticsData.expense_trend) return;

  const trendChartCanvas = document.getElementById("trendChart");
  const trend = analyticsData.expense_trend;

  const labels = trend.map(t => t.month || "Unknown");
  const incomeData = trend.map(t => t.data.Income || 0);
  const expenseData = trend.map(t => t.data.Expense || 0);

  if (trendChart) trendChart.destroy();

  trendChart = new Chart(trendChartCanvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Income (Collected)',
          data: incomeData,
          backgroundColor: 'rgba(76, 175, 80, 0.7)', // Green
          borderColor: '#388E3C',
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: 'Expenses (Disbursed)',
          data: expenseData,
          backgroundColor: 'rgba(244, 67, 54, 0.7)', // Red
          borderColor: '#D32F2F',
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: true, position: 'top' },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) { label += ': '; }
              if (context.parsed.y !== null) { label += '₱' + context.parsed.y.toFixed(2); }
              return label;
            }
          }
        }
      },
      scales: {
        x: { stacked: false }, // Set to true if you want bars stacked on top of each other
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) { return '₱' + value.toLocaleString(); }
          }
        }
      }
    }
  });
}

function displayCategoryTable() {
  if (!analyticsData || !analyticsData.category_totals) return;

  const tbody = document.getElementById("categoriesTableBody");
  const categories = analyticsData.category_totals;
  const totalSpent = categories.reduce((sum, cat) => sum + cat.total, 0);

  tbody.innerHTML = "";
  categories.forEach(cat => {
    const percentage = totalSpent > 0 ? ((cat.total / totalSpent) * 100).toFixed(1) : 0;
    const row = `
      <tr>
        <td>${cat._id.category_name || "Uncategorized"}</td>
        <td>₱${Number(cat.total).toFixed(2)}</td>
        <td>${cat.count}</td>
        <td>
          <div class="percentage-bar">
            <div class="percentage-fill" style="width: ${percentage}%"></div>
            <span class="percentage-text">${percentage}%</span>
          </div>
        </td>
      </tr>
    `;
    tbody.innerHTML += row;
  });

  if (categories.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">No transactions recorded</td></tr>';
  }
}

async function seedData() {
  const userId = localStorage.getItem("user_id");
  
  if (!confirm("Load sample data? This will add 90 sample expenses (15 per category) for testing.")) {
    return;
  }

  try {
    const res = await fetch(`${api}/seed-data/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    if (!res.ok) {
      const data = await res.json();
      alert(`⚠️ ${data.error || "Failed to load sample data"}`);
      return;
    }

    const data = await res.json();
    alert(`✅ Sample data loaded!\n${data.message}\nCategories: ${data.categories_created}, Expenses: ${data.expenses_created}`);
    loadAnalytics();
  } catch (error) {
    console.error("Error loading sample data:", error);
    alert("Error loading sample data");
  }
}

const darkModeToggle = document.getElementById("darkModeToggle");
if (darkModeToggle) {
  darkModeToggle.addEventListener("change", () => {
    setTimeout(() => {
      if (categoryChart) categoryChart.resize();
      if (trendChart) trendChart.resize();
    }, 100);
  });
}
