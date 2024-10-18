document.addEventListener("DOMContentLoaded", function () {
  // Add a confirmation dialog for delete actions
  document.querySelectorAll(".delete-button").forEach(function (button) {
    button.addEventListener("click", function (e) {
      if (!confirm("Are you sure you want to delete this item?")) {
        e.preventDefault();
      }
    });
  });

  // Example for handling form submission via AJAX
  document.querySelectorAll(".ajax-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const url = form.getAttribute("action");
      const formData = new FormData(form);

      fetch(url, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.reload(); // Reload page on success
          } else {
            alert("There was an error submitting the form.");
          }
        });
    });
  });

  // Additional scripts (e.g., handling form validation or UI changes)
});

// Handle AJAX form submissions
document.querySelectorAll(".ajax-form").forEach(function (form) {
  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent the form from submitting the traditional way
    const url = form.getAttribute("action");
    const formData = new FormData(form);

    fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Product successfully created!");
          window.location.href = data.redirect_url; // Redirect or refresh page
        } else {
          alert("There was an error.");
        }
      });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const deleteModal = document.getElementById("deleteModal");
  const confirmDeleteButton = document.getElementById("confirmDelete");
  const cancelDeleteButton = document.getElementById("cancelDelete");

  document.querySelectorAll(".delete-button").forEach(function (button) {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const url = this.getAttribute("href");

      deleteModal.style.display = "block"; // Show the modal

      // Confirm deletion
      confirmDeleteButton.onclick = function () {
        window.location.href = url; // Proceed with the deletion
      };

      // Cancel deletion
      cancelDeleteButton.onclick = function () {
        deleteModal.style.display = "none"; // Hide the modal
      };
    });
  });
});
