
const adminLoginForm = document.getElementById("adminLoginForm");

adminLoginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("adminEmail").value.trim();
    const password = document.getElementById("adminPassword").value;
    const message = document.getElementById("adminLoginMessage");

    message.textContent = "Checking login details...";
    message.style.color = "blue";

    try {
        const response = await fetch("http://127.0.0.1:5000/api/admin/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            sessionStorage.setItem("dagaAdminLoggedIn", "true");
            sessionStorage.setItem("dagaAdmin", JSON.stringify(data.admin));

            message.textContent = "Login successful! Opening dashboard...";
            message.style.color = "green";

            setTimeout(function() {
                window.location.href = "admin-dashboard.html";
            }, 1000);

        } else {
            message.textContent = data.message || "Invalid admin email or password.";
            message.style.color = "red";
        }

    } catch (error) {
        console.error("Admin login error:", error);

        message.textContent = "Cannot connect to the server. Please try again.";
        message.style.color = "red";
    }
});
