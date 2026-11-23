
// Check admin login
if (sessionStorage.getItem("dagaAdminLoggedIn") !== "true") {
    window.location.replace("admin-login.html");
}

// Read data safely from localStorage
function getStoredData(key) {
    try {
        return JSON.parse(localStorage.getItem(key)) || [];
    } catch (error) {
        console.error("Could not read " + key, error);
        return [];
    }
}

// Update dashboard statistics

async function updateAdminStats() {
    try {
        const response = await fetch(window.DAGA_API_BASE + "/api/admin/dashboard");

        if (!response.ok) {
            throw new Error("Could not load dashboard statistics.");
        }

        const data = await response.json();

        document.getElementById("touristCount").textContent = data.total_tourists;
        document.getElementById("businessCount").textContent = data.total_business_owners;
        document.getElementById("pendingCount").textContent = data.pending_business_owners;
        document.getElementById("serviceCount").textContent = data.total_services;
        document.getElementById("bookingCount").textContent = data.total_bookings;

    } catch (error) {
        console.error("Dashboard statistics error:", error);
    }
}


// Display registered tourists

async function displayTourists() {
    const touristList = document.getElementById("touristList");

    touristList.replaceChildren();

    try {
        const response = await fetch(window.DAGA_API_BASE + "/api/admin/tourists");

        if (!response.ok) {
            throw new Error("Could not load tourists.");
        }

        const tourists = await response.json();

        if (tourists.length === 0) {
            const empty = document.createElement("p");
            empty.className = "admin-empty";
            empty.textContent = "No tourists have registered yet.";
            touristList.appendChild(empty);
            return;
        }

        tourists.forEach(function(tourist) {
            const card = document.createElement("div");
            card.className = "admin-item";

            const name = document.createElement("h3");
            name.textContent = tourist.name || "Tourist";

            const email = document.createElement("p");
            email.textContent = "Email: " + (tourist.email || "Not provided");

            const phone = document.createElement("p");
            phone.textContent = "Phone: " + (tourist.phone || "Not provided");

            card.append(name, email, phone);
            touristList.appendChild(card);
        });

    } catch (error) {
        console.error("Tourist loading error:", error);

        const message = document.createElement("p");
        message.className = "admin-empty";
        message.textContent = "Could not load tourists. Please try again.";
        touristList.appendChild(message);
    }
}


// Display registered businesses

async function displayBusinesses() {
    const businessList = document.getElementById("businessList");

    businessList.replaceChildren();

    try {
        const response = await fetch(window.DAGA_API_BASE + "/api/admin/business-owners");

        if (!response.ok) {
            throw new Error("Could not load businesses.");
        }

        const owners = await response.json();

        if (owners.length === 0) {
            const empty = document.createElement("p");
            empty.className = "admin-empty";
            empty.textContent = "No businesses have registered yet.";
            businessList.appendChild(empty);
            return;
        }

        owners.forEach(function(owner) {
            const card = document.createElement("div");
            card.className = "admin-item";

            const name = document.createElement("h3");
            name.textContent = owner.business_name || "Business";

            const ownerName = document.createElement("p");
            ownerName.textContent = "Owner: " + (owner.name || "Not provided");

            const email = document.createElement("p");
            email.textContent = "Email: " + (owner.email || "Not provided");

            const phone = document.createElement("p");
            phone.textContent = "Phone: " + (owner.phone || "Not provided");

            const statusValue = owner.status || "Pending";

            const status = document.createElement("span");
            status.className = "admin-status";

            if (statusValue.toLowerCase() === "approved") {
                status.classList.add("approved");
            } else if (statusValue.toLowerCase() === "rejected") {
                status.classList.add("rejected");
            }

            status.textContent = "Status: " + statusValue;

            card.append(name, ownerName, email, phone, status);

            if (statusValue.toLowerCase() === "pending") {
                const actions = document.createElement("div");
                actions.className = "admin-actions";

                const approveButton = document.createElement("button");
                approveButton.className = "approve-btn";
                approveButton.textContent = "Approve";

                approveButton.addEventListener("click", function() {
                    updateBusinessStatus(owner.id, "Approved");
                });

                const rejectButton = document.createElement("button");
                rejectButton.className = "reject-btn";
                rejectButton.textContent = "Reject";

                rejectButton.addEventListener("click", function() {
                    updateBusinessStatus(owner.id, "Rejected");
                });

                actions.append(approveButton, rejectButton);
                card.appendChild(actions);
            }

            businessList.appendChild(card);
        });

    } catch (error) {
        console.error("Business loading error:", error);

        const message = document.createElement("p");
        message.className = "admin-empty";
        message.textContent = "Could not load businesses. Please try again.";
        businessList.appendChild(message);
    }
}


// Approve or reject a business

async function updateBusinessStatus(ownerId, newStatus) {
    if (!ownerId) {
        alert("Business ID is missing.");
        return;
    }

    const confirmed = confirm(
        "Are you sure you want to " + newStatus.toLowerCase() +
        " this business?"
    );

    if (!confirmed) return;

    try {
        const response = await fetch(
            window.DAGA_API_BASE + "/api/admin/business-owners/" +
            ownerId + "/status",
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Could not update business status.");
        }

        alert("Business " + newStatus.toLowerCase() + " successfully.");

        renderAdminDashboard();

    } catch (error) {
        console.error("Business status update error:", error);
        alert(error.message || "Something went wrong. Please try again.");
    }
}


// Render all admin dashboard content
function renderAdminDashboard() {
    updateAdminStats();
    displayTourists();
    displayBusinesses();
}

// Admin logout
function adminLogout() {
    const confirmed = confirm("Are you sure you want to logout?");

    if (confirmed) {
        sessionStorage.removeItem("dagaAdminLoggedIn");
        window.location.replace("admin-login.html");
    }
}

// Initial dashboard load
renderAdminDashboard();
