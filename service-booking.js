
const API_BASE = "http://127.0.0.1:5000";

const params = new URLSearchParams(window.location.search);
const serviceId = params.get("id");

const loggedInUser = JSON.parse(
    localStorage.getItem("dagaLoggedInUser") || "null"
);

const form = document.getElementById("serviceBookingForm");
const message = document.getElementById("bookingFormMessage");
const dateInput = document.getElementById("bookingDate");

let service = null;
let owner = null;

async function loadBookingPage() {

    if (!loggedInUser) {
        form.hidden = true;
        message.textContent = "Please login before booking.";
        return;
    }

    if (!loggedInUser.id) {
        form.hidden = true;
        message.textContent = "Tourist ID missing. Please login again.";
        return;
    }

    try {
        // Fetch approved services
        const servicesResponse = await fetch(
            `${API_BASE}/api/services`
        );

        const servicesData = await servicesResponse.json();

        if (!servicesResponse.ok) {
            throw new Error("Could not load services.");
        }

        service = servicesData.services.find(
            item => String(item.id) === String(serviceId)
        );

        if (!service) {
            throw new Error("Service not found or not approved.");
        }

        // Fetch business owner details
        const ownerResponse = await fetch(
            `${API_BASE}/api/business/profile/${service.owner_id}`
        );

        const ownerData = await ownerResponse.json();

        if (!ownerResponse.ok) {
            throw new Error("Could not load business details.");
        }

        owner = ownerData.owner;

        // Set minimum booking date
        const today = new Date();

        const localToday = new Date(
            today.getTime() - today.getTimezoneOffset() * 60000
        ).toISOString().split("T")[0];

        dateInput.min = localToday;

        // Display service details
        document.getElementById("bookingServiceName").textContent =
            service.name;

        document.getElementById("bookingBusinessName").textContent =
            "Business: " + owner.business_name;

        document.getElementById("bookingServicePrice").textContent =
            "Price: ₹" + service.price + " / " + service.unit;

        // Fill tourist details
        document.getElementById("touristName").value =
            loggedInUser.name || "";

        document.getElementById("touristEmail").value =
            loggedInUser.email || "";

        document.getElementById("touristPhone").value =
            loggedInUser.phone || "";

        // Show booking form
        form.hidden = false;

    } catch (error) {
        form.hidden = true;
        message.textContent = error.message;
    }
}


// Submit booking to MySQL
form.addEventListener("submit", async function(event) {

    event.preventDefault();

    if (!service || !owner) {
        message.textContent = "Service details are unavailable.";
        return;
    }

    const today = new Date();

    const localToday = new Date(
        today.getTime() - today.getTimezoneOffset() * 60000
    ).toISOString().split("T")[0];

    if (!dateInput.value || dateInput.value < localToday) {
        message.textContent = "Please select a valid booking date.";
        return;
    }

    const guests = Number(
        document.getElementById("bookingGuests").value
    );

    if (!Number.isInteger(guests) || guests < 1) {
        message.textContent = "Please enter at least one guest.";
        return;
    }

    const bookingData = {
        tourist_id: loggedInUser.id,
        service_id: service.id,
        booking_date: dateInput.value,
        guests: guests,
        tourist_name: document.getElementById("touristName").value.trim(),
        tourist_email: loggedInUser.email,
        tourist_phone: document.getElementById("touristPhone").value.trim(),
        message: document.getElementById("bookingMessage").value.trim()
    };

    try {
        message.textContent = "Submitting your booking...";

        const response = await fetch(
            `${API_BASE}/api/bookings`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bookingData)
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || "Booking failed.");
        }

        // Redirect using actual MySQL booking ID
        window.location.href =
            "booking-confirmation.html?id=" +
            encodeURIComponent(result.booking_id);

    } catch (error) {
        message.textContent = error.message;
    }

});


// Load service and business details
loadBookingPage();
