if (document.getElementById("loginForm")) {
  document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${api}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: document.getElementById("loginUsername").value,
          password: document.getElementById("loginPassword").value,
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        alert(errorData.error || "Invalid username or password.");
        return;
      }
      
      const data = await res.json();
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("username", document.getElementById("loginUsername").value);
      window.location.href = "dashboard.html";
    } catch (error) {
      console.error("Login error:", error);
      alert("An error occurred. Please try again.");
    }
  });
}

if (document.getElementById("registerForm")) {
  document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${api}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: document.getElementById("registerUsername").value,
          email: document.getElementById("email").value,
          password: document.getElementById("password").value,
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        alert(errorData.error || "Failed to register.");
        return;
      }
      
      const data = await res.json();
      alert("Registration successful!");
      window.location.href = "login.html";
    } catch (error) {
      console.error("Registration error:", error);
      alert("An error occurred. Please try again.");
    }
  });
}
