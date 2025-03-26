document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("login-form").addEventListener("submit", function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();
        const errorMessage = document.getElementById("error-message");

        // Example static credentials (Replace with backend authentication)
        const validUsername = "admin";
        const validPassword = "secret";

        if (username === validUsername && password === validPassword) {
            window.location.href = "/dashboard"; // Redirect to dashboard or home page
        } else {
            errorMessage.textContent = "Invalid username or password!";
        }
    });
});
