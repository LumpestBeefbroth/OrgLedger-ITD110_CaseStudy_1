if (document.getElementById("loginForm")) {
  document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const res = await fetch(`${api}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.getElementById("loginUsername").value,
        password: document.getElementById("loginPassword").value,
      })
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("username", document.getElementById("loginUsername").value);
      window.location.href = "dashboard.html";
    } else {
      alert("Invalid username or password.");
    }
  });
}

if (document.getElementById("registerForm")) {
  document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const res = await fetch(`${api}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.getElementById("registerUsername").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      })
    });
    const data = await res.json();
    if (res.ok) {
      alert("Registration successful!");
      window.location.href = "login.html";
    } else {
      alert(data.error || "Failed to register.");
    }
  });
}
