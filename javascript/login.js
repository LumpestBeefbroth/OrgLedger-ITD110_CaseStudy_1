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
      
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (err) {
        alert("Server Error: " + text.substring(0, 200));
        return;
      }
      
      if (!res.ok) {
        alert(data.error || "Invalid username or password.");
        return;
      }
      
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("username", document.getElementById("loginUsername").value);
      window.location.href = "dashboard.html";
    } catch (error) {
      alert("Network error. Please check your connection and try again.");
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
      
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (err) {
        alert("Server Error: " + text.substring(0, 200));
        return;
      }
      
      if (!res.ok) {
        alert(data.error || "Failed to register.");
        return;
      }
      
      alert("Registration successful!");
      window.location.href = "login.html";
    } catch (error) {
      alert("Network error. Please check your connection and try again.");
    }
  });
}
