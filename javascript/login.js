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
        console.error("[LOGIN] Server sent non-JSON response:", text);
        alert("Server Error: " + text.substring(0, 200));
        return;
      }
      
      if (!res.ok) {
        console.error("[LOGIN] Server error:", data);
        alert(data.error || "Invalid username or password.");
        return;
      }
      
      console.log("[LOGIN] Login successful");
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("username", document.getElementById("loginUsername").value);
      window.location.href = "dashboard.html";
    } catch (error) {
      console.error("[LOGIN] Fetch error:", error);
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
        console.error("[REGISTER] Server sent non-JSON response:", text);
        alert("Server Error: " + text.substring(0, 200));
        return;
      }
      
      if (!res.ok) {
        console.error("[REGISTER] Server error:", data);
        alert(data.error || "Failed to register.");
        return;
      }
      
      console.log("[REGISTER] Registration successful");
      alert("Registration successful!");
      window.location.href = "login.html";
    } catch (error) {
      console.error("[REGISTER] Fetch error:", error);
      alert("Network error. Please check your connection and try again.");
    }
  });
}
