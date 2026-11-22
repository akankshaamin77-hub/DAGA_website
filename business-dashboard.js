

const loggedOwner = JSON.parse(localStorage.getItem("dagaLoggedInOwner"));

if (!loggedOwner || !loggedOwner.id) {
    alert("Please login as a business owner.");
    window.location.href = "business-login.html";
} else {
    async function loadBusinessProfile() {
        try {
            const response = await fetch(
                "http://127.0.0.1:5000/api/business/profile/" + loggedOwner.id
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Failed to load profile.");
            }

            const owner = data.owner;

            document.getElementById("dashboardBusinessName").textContent =
                owner.business_name || "Not provided";

            document.getElementById("dashboardLocation").textContent =
                "Not provided";

            document.getElementById("dashboardCategory").textContent =
                "Not provided";

            document.getElementById("dashboardEmail").textContent =
                owner.email || "Not provided";
        } catch (error) {
            console.error("Profile loading error:", error);
        }
    }

    loadBusinessProfile();
}


// UPDATE BOOKING STATUS
function updateRequest(status) {

    localStorage.setItem("dagaBookingStatus", status);

    displayBookingStatus(status);
}

// DISPLAY STATUS AND HIDE BUTTONS
function displayBookingStatus(status) {

    const statusElement = document.getElementById("bookingStatus");
    const actionsElement = document.getElementById("bookingActions");

    if (statusElement) {
        statusElement.textContent =
            status === "confirmed" ? "Accepted" : "Rejected";
    }

    if (actionsElement) {
        actionsElement.style.display = "none";
    }
}

// RESTORE SAVED STATUS
const savedStatus = localStorage.getItem("dagaBookingStatus");

if (savedStatus) {
    displayBookingStatus(savedStatus);
}

// LOGOUT
function businessLogout() {
    localStorage.removeItem("dagaLoggedInOwner");
    window.location.href = "business-login.html";
}
