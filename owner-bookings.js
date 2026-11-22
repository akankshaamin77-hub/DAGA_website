
const loggedOwner = JSON.parse(
    localStorage.getItem("dagaLoggedInOwner")
);

const ownerBookingsList = document.getElementById("ownerBookingsList");
const ownerBookingFilter = document.getElementById("ownerBookingFilter");

if (!loggedOwner) {
    window.location.replace("business-login.html");
} else if (ownerBookingsList && ownerBookingFilter) {

    
async function getMyBookings() {
    try {
        const response = await fetch(
            "http://127.0.0.1:5000/api/bookings/business/" + loggedOwner.id
        );

        const bookings = await response.json();

        if (!response.ok) {
            throw new Error(bookings.message || "Failed to load bookings.");
        }

        return bookings;
    } catch (error) {
        console.error("Error loading bookings:", error);
        alert("Could not load booking requests. Please try again.");
        return [];
    }
}


    
function updateOwnerBookingStats(bookings) {
    document.getElementById("ownerTotalBookings").textContent =
        bookings.length;

    document.getElementById("ownerPendingBookings").textContent =
        bookings.filter(b =>
            (b.status || "Pending").toLowerCase() === "pending"
        ).length;

    document.getElementById("ownerAcceptedBookings").textContent =
        bookings.filter(b =>
            (b.status || "").toLowerCase() === "accepted"
        ).length;
}


async function updateBookingStatus(bookingId, newStatus) {
    if (!confirm("Are you sure you want to " +
        newStatus.toLowerCase() + " this booking?")) {
        return;
    }

    try {
        const response = await fetch(
            "http://127.0.0.1:5000/api/bookings/" + bookingId + "/status",
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    owner_id: loggedOwner.id,
                    status: newStatus
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Could not update booking.");
        }

        alert("Booking " + newStatus.toLowerCase() + " successfully!");

        await renderOwnerBookings();

    } catch (error) {
        console.error("Booking status error:", error);
        alert(error.message);
    }
}



async function renderOwnerBookings() {
    const bookings = await getMyBookings();
    const selectedStatus = ownerBookingFilter.value.toLowerCase();

    const filteredBookings = bookings.filter(function(booking) {
        const status = (booking.status || "Pending").toLowerCase();

        return selectedStatus === "all" ||
            status === selectedStatus;
    });

    ownerBookingsList.replaceChildren();

    if (filteredBookings.length === 0) {
        const empty = document.createElement("p");
        empty.className = "service-empty-message";
        empty.textContent = "No booking requests found.";
        ownerBookingsList.appendChild(empty);

        updateOwnerBookingStats(bookings);
        return;
    }

    filteredBookings.forEach(function(booking) {
        const card = document.createElement("div");
        card.className = "managed-service-card";

        const title = document.createElement("h3");
        title.textContent = booking.service_name || "Service";
        card.appendChild(title);

        const details = [
            "Booking ID: " + booking.id,
            "Tourist: " + (booking.tourist_name || "Not available"),
            "Email: " + (booking.tourist_email || "Not available"),
            "Phone: " + (booking.tourist_phone || "Not available"),
            "Date: " + (booking.booking_date || "Not available"),
            "Number of people: " + (booking.guests || "Not available"),
            "Message: " + (booking.message || "No message"),
            "Status: " + (booking.status || "Pending")
        ];

        details.forEach(function(detail) {
            const paragraph = document.createElement("p");
            paragraph.textContent = detail;
            card.appendChild(paragraph);
        });

        const status = (booking.status || "Pending").toLowerCase();

        if (status === "pending") {
            const acceptButton = document.createElement("button");
            acceptButton.type = "button";
            acceptButton.textContent = "Accept";

            acceptButton.addEventListener("click", function() {
                updateBookingStatus(booking.id, "Accepted");
            });

            const rejectButton = document.createElement("button");
            rejectButton.type = "button";
            rejectButton.textContent = "Reject";
            rejectButton.className = "delete-service-btn";

            rejectButton.addEventListener("click", function() {
                updateBookingStatus(booking.id, "Rejected");
            });

            card.append(acceptButton, rejectButton);
        }

        ownerBookingsList.appendChild(card);
    });

    updateOwnerBookingStats(bookings);
}


    ownerBookingFilter.addEventListener("change", function() {
    renderOwnerBookings();
});

renderOwnerBookings();
}

// Logout
function businessLogout() {
    if (confirm("Are you sure you want to logout?")) {
        localStorage.removeItem("dagaLoggedInOwner");
        window.location.replace("business-login.html");
    }
}

