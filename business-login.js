
const businessLoginForm = document.getElementById("businessLoginForm");

businessLoginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("businessEmail").value.trim();
    const password = document.getElementById("businessPassword").value;
    const message = document.getElementById("businessLoginMessage");

    try {
        const response = await fetch(
            window.DAGA_API_BASE + "/api/business/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Invalid email or password.");
        }

        localStorage.setItem(
            "dagaLoggedInOwner",
            JSON.stringify({
                id: data.id,
                ownerName: data.name,
                businessName: data.business_name,
                email: data.email
            })
        );

        message.textContent = "Login successful!";
        message.style.color = "green";

        setTimeout(function() {
            window.location.href = "business-dashboard.html";
        }, 1000);

    } catch (error) {
        console.error("Business login error:", error);

        message.textContent = error.message || "Unable to connect to server.";
        message.style.color = "red";
    }
});
