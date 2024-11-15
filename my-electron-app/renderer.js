const { ipcRenderer } = require('electron');

function validateRegister() {
    var name = document.getElementById("nameInput").value;
    var id = document.getElementById("idInput").value.toUpperCase();
    var password = document.getElementById("passwordInput").value;
    var email = document.getElementById("emailInput").value;
    var outputBox = document.getElementById("outputBox"); // Get output box element
    
    var isValid = true;
    // Check if all four details are provided
    if (name.trim() === "" || id.trim() === "" || password.trim() === "" || email.trim() === "") {
        document.getElementById("outputBox").value = "Please provide all details";
        isValid = false;
        return; // Exit the function if any detail is missing
    }

    // Validate ID
    if (!/^[A-Z]{4}$/.test(id)) {
        document.getElementById("outputBox").value = "ID must be 4 uppercase letters";
        isValid = false;
    } 

    // Validate Password
    if (!/^\d{4}$/.test(password)) {
        document.getElementById("outputBox").value = "Password must be 4 digits";
        isValid = false;
    } 

    // Validate Email
    if (!email.includes('@')) {
        document.getElementById("outputBox").value = "Invalid email format";
        isValid = false;
    } 

    if (isValid) {
        document.getElementById("outputBox").value = "Software Initialization in Process, Check CMD";
        outputBox.style.color = "green"; // Change text color to green

        ipcRenderer.send('run-script', { name, id, password, email }); // Sending data to main process
    }
}

// Function to close the window
function closeWindow() {
    window.close();
}
