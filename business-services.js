
const currentOwner = JSON.parse(
    localStorage.getItem("dagaLoggedInOwner")
);

if (!currentOwner) {
    window.location.replace("business-login.html");
}

const serviceForm = document.getElementById("serviceForm");
const serviceName = document.getElementById("serviceName");
const serviceCategory = document.getElementById("serviceCategory");
const serviceDescription = document.getElementById("serviceDescription");
const servicePrice = document.getElementById("servicePrice");
const serviceUnit = document.getElementById("serviceUnit");
const serviceMessage = document.getElementById("serviceMessage");
const managedServicesList = document.getElementById("managedServicesList");
const serviceSubmitButton = document.getElementById("serviceSubmitButton");
const cancelEditButton = document.getElementById("cancelEditButton");

let editingServiceId = null;

let allServices = JSON.parse(localStorage.getItem("dagaServices")) || [];

function saveServices() {
    localStorage.setItem("dagaServices", JSON.stringify(allServices));
}

function getOwnerServices() {
    return allServices.filter(function(service) {
        return service.ownerEmail === currentOwner.email;
    });
}

function resetServiceForm() {
    serviceForm.reset();
    editingServiceId = null;
    serviceSubmitButton.textContent = "Add Service";
    document.getElementById("serviceFormTitle").textContent = "Add a New Service";
    cancelEditButton.hidden = true;
}


async function displayServices() {
    managedServicesList.replaceChildren();

    try {
        const response = await fetch(
            window.DAGA_API_BASE + "/api/business/services/" + currentOwner.id
        );

        if (!response.ok) {
            throw new Error("Could not load your services.");
        }

        const data = await response.json();
        const ownerServices = data.services;

        if (ownerServices.length === 0) {
            const emptyMessage = document.createElement("p");
            emptyMessage.className = "service-empty-message";
            emptyMessage.textContent = "You haven't added any services yet.";
            managedServicesList.appendChild(emptyMessage);
            return;
        }

        ownerServices.forEach(function(service) {
            const card = document.createElement("div");
            card.className = "managed-service-card";

            const title = document.createElement("h3");
            title.textContent = service.name;

            const category = document.createElement("p");
            category.textContent = "Category: " + service.category;

            const description = document.createElement("p");
            description.textContent = service.description;

            const price = document.createElement("p");
            price.textContent = "Price: ₹" + service.price + " / " + service.unit;

            const status = document.createElement("p");
            status.textContent = "Status: " + service.status;

            const editButton = document.createElement("button");
            editButton.textContent = "Edit";
            editButton.addEventListener("click", function() {
                editService(service.id);
            });

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.className = "delete-service-btn";
            deleteButton.addEventListener("click", function() {
                deleteService(service.id);
            });

            card.append(
                title, category, description, price, status,
                editButton, deleteButton
            );

            managedServicesList.appendChild(card);
        });

    } catch (error) {
        console.error("Service loading error:", error);

        const message = document.createElement("p");
        message.className = "service-empty-message";
        message.textContent = "Could not load services. Please try again.";
        managedServicesList.appendChild(message);
    }
}


serviceForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const serviceData = {
        owner_id: currentOwner.id,
        name: serviceName.value.trim(),
        category: serviceCategory.value,
        description: serviceDescription.value.trim(),
        price: Number(servicePrice.value),
        unit: serviceUnit.value
    };

    if (!serviceData.name || !serviceData.description ||
        !serviceData.category || !serviceData.unit ||
        serviceData.price < 0 || !Number.isFinite(serviceData.price)) {
        serviceMessage.textContent = "Please enter valid service details.";
        serviceMessage.style.color = "red";
        return;
    }

    try {
        const url = editingServiceId !== null
            ? window.DAGA_API_BASE + "/api/business/services/" + editingServiceId
            : window.DAGA_API_BASE + "/api/business/services";

        const response = await fetch(url, {
            method: editingServiceId !== null ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(serviceData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Could not save service.");
        }

        serviceMessage.textContent = data.message;
        serviceMessage.style.color = "green";

        resetServiceForm();
        displayServices();

    } catch (error) {
        console.error("Service save error:", error);
        serviceMessage.textContent = error.message;
        serviceMessage.style.color = "red";
    }
});



async function editService(id) {
    try {
        const response = await fetch(
            window.DAGA_API_BASE + "/api/business/services/" + currentOwner.id
        );

        if (!response.ok) {
            throw new Error("Could not load service details.");
        }

        const data = await response.json();

        const service = data.services.find(function(item) {
            return Number(item.id) === Number(id);
        });

        if (!service) {
            alert("Service not found.");
            return;
        }

        editingServiceId = service.id;

        serviceName.value = service.name;
        serviceCategory.value = service.category;
        serviceDescription.value = service.description;
        servicePrice.value = service.price;
        serviceUnit.value = service.unit;

        serviceSubmitButton.textContent = "Update Service";
        document.getElementById("serviceFormTitle").textContent = "Edit Service";
        cancelEditButton.hidden = false;

        window.scrollTo({ top: 0, behavior: "smooth" });

    } catch (error) {
        console.error("Edit service error:", error);
        alert(error.message);
    }
}



async function deleteService(id) {
    const confirmDelete = confirm("Do you want to delete this service?");

    if (!confirmDelete) return;

    try {
        const response = await fetch(
            window.DAGA_API_BASE + "/api/business/services/" + id,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    owner_id: currentOwner.id
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Could not delete service.");
        }

        serviceMessage.textContent = "Service deleted successfully!";
        serviceMessage.style.color = "green";

        displayServices();

    } catch (error) {
        console.error("Delete service error:", error);
        serviceMessage.textContent = error.message;
        serviceMessage.style.color = "red";
    }
}


cancelEditButton.addEventListener("click", resetServiceForm);

function businessLogout() {
    if (confirm("Are you sure you want to logout?")) {
        localStorage.removeItem("dagaLoggedInOwner");
        window.location.replace("business-login.html");
    }
}

if (currentOwner) {
    displayServices();
}
